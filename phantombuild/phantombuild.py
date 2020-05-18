"""Phantom build."""

import copy
import logging
import pathlib
import shutil
import subprocess
import sys
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List, Union

import tomlkit


class RepoError(Exception):
    """Exception for dealing with Phantom git repository."""


class PatchError(Exception):
    """Exception for dealing with patching Phantom."""


class CompileError(Exception):
    """Exception for dealing with compiling Phantom."""


class SetupError(Exception):
    """Exception for dealing with setting up a Phantom calculation."""


class HDF5LibraryNotFound(Exception):
    """Cannot find HDF5 library."""


class ScheduleError(Exception):
    """Exception for dealing with scheduling a Phantom calculation."""


class TOMLError(Exception):
    """Exception for dealing with reading TOML files."""


def _setup_logger(filename: Path = None) -> Logger:

    if filename is None:
        filename = pathlib.Path('.phantom-build.log').expanduser()

    logger = logging.getLogger('phantom-build')

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(filename, mode='w')

    console_format = logging.Formatter(
        '%(name)s %(levelname)s: %(funcName)s - %(message)s'
    )
    file_format = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s: %(funcName)s - %(message)s',
        '%Y-%m-%d %H:%M:%S',
    )
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.setLevel(logging.INFO)

    return logger


logger = _setup_logger()


def get_phantom(path: Union[Path, str]) -> bool:
    """Get Phantom repository.

    Parameters
    ----------
    path
        The path to the Phantom repository.

    Returns
    -------
    bool
        Success or fail as boolean.
    """
    _path = _resolved_path(path)
    logger.info('Getting Phantom repository')
    logger.info(f'path: {_path}')

    if not _path.exists():
        logger.info('Cloning fresh copy of Phantom')
        result = subprocess.run(
            [
                'git',
                'clone',
                'https://bitbucket.org/danielprice/phantom.git',
                _path.stem,
            ],
            cwd=_path.parent,
        )
        if result.returncode != 0:
            logger.error('Phantom clone failed')
            raise RepoError('Fail to clone repo')
        else:
            logger.info('Phantom successfully cloned')
    else:
        if not (
            subprocess.run(
                ['git', 'config', '--local', '--get', 'remote.origin.url'],
                cwd=_path,
                stdout=subprocess.PIPE,
                text=True,
            ).stdout.strip()
            in [
                'git@bitbucket.org:danielprice/phantom',
                'git@bitbucket.org:danielprice/phantom.git',
                'https://bitbucket.org/danielprice/phantom',
                'https://bitbucket.org/danielprice/phantom.git',
            ]
        ):
            msg = f'{path} is not Phantom'
            logger.error(msg)
            raise RepoError(msg)
        else:
            logger.info('Phantom already cloned')

    return True


def checkout_phantom_version(path: Union[Path, str], version: str) -> bool:
    """Check out a particular Phantom version.

    Parameters
    ----------
    path
        The path to the Phantom repository.
    version
        The required Phantom version specified by git commit hash.

    Returns
    -------
    bool
        Success or fail as boolean.
    """
    _path = _resolved_path(path)
    logger.info('Getting required Phantom version')

    # Check git commit hash
    phantom_git_commit_hash = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], cwd=_path, stdout=subprocess.PIPE, text=True,
    ).stdout.strip()
    short_hash = subprocess.run(
        ['git', 'rev-parse', '--short', version],
        cwd=_path,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    if phantom_git_commit_hash != version:
        logger.info('Checking out required Phantom version')
        logger.info(f'Git commit hash: {short_hash}')
        result = subprocess.run(['git', 'checkout', version], cwd=_path)
        if result.returncode != 0:
            msg = 'Failed to checkout required version'
            logger.error(msg)
            raise RepoError(msg)
        else:
            logger.info('Successfully checked out required version')
    else:
        logger.info('Required version of Phantom already checked out')
        logger.info(f'Git commit hash: {short_hash}')

    # Check if clean
    git_status = subprocess.run(
        ['git', 'status', '--porcelain'], cwd=_path, stdout=subprocess.PIPE, text=True,
    ).stdout.strip()
    if not git_status == '':
        logger.info('Cleaning repository')
        results = list()
        results.append(subprocess.run(['git', 'reset', 'HEAD'], cwd=_path))
        results.append(subprocess.run(['git', 'clean', '--force'], cwd=_path))
        results.append(subprocess.run(['git', 'checkout', '--', '*'], cwd=_path))
        if any(result.returncode != 0 for result in results):
            msg = 'Failed to clean repo'
            logger.error(msg)
            raise RepoError(msg)
        else:
            logger.info('Successfully cleaned repo')

    return True


def patch_phantom(path: Union[Path, str], patch: Union[Path, str]) -> bool:
    """Apply patch to Phantom.

    Parameters
    ----------
    path
        The path to the Phantom repository.
    patch
        The path to the patch file, if required.

    Returns
    -------
    bool
        Success or fail as boolean.
    """
    _path = _resolved_path(path)
    _patch = _resolved_path(patch)

    logger.info('Patching Phantom')
    logger.info(f'Patch file: {_patch}')

    result = subprocess.run(['git', 'apply', _patch], cwd=_path)
    if result.returncode != 0:
        msg = 'Failed to patch Phantom'
        logger.error(msg)
        raise PatchError(msg)
    else:
        logger.info('Successfully patched Phantom')

    return True


def build_phantom(
    path: Union[Path, str],
    setup: str,
    system: str,
    hdf5_path: Union[Path, str] = None,
    extra_options: Dict[str, str] = None,
) -> bool:
    """Build Phantom.

    Parameters
    ----------
    path
        The path to the Phantom repository.
    setup
        The Phantom setup, e.g. 'disc', 'dustybox', etc.
    system
        The compiler as specified in the Phantom makefile, e.g.
        'gfortran' or 'ifort'.
    hdf5_path
        The path to the HDF5 installation, or if None, do not compile
        with HDF5.
    extra_options
        Extra options to pass to make. This values in this dictionary
        should be strings only.

    Returns
    -------
    bool
        Success or fail as boolean.
    """
    _path = _resolved_path(path)
    logger.info('Building Phantom')

    make_command = ['make', 'SETUP=' + setup, 'SYSTEM=' + system]

    if hdf5_path is not None:
        _hdf5_path = _resolved_path(hdf5_path)
        if not _hdf5_path.exists():
            raise HDF5LibraryNotFound('Cannot determine HDF5 library location')
        make_command += ['HDF5=yes', 'HDF5ROOT=' + str(_hdf5_path.resolve())]

    if extra_options is not None:
        make_command += [key + '=' + val for key, val in extra_options.items()]

    build_log = _path / 'build' / 'build_output.log'
    with open(build_log, 'w') as fp:
        process = subprocess.Popen(
            make_command,
            cwd=_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            fp.write(line)
        process.communicate()[0]

    if process.returncode != 0:
        msg = 'Phantom failed to compile'
        logger.error(msg)
        logger.info(f'See "{build_log.name}" in Phantom build directory for output')
        raise CompileError(msg)
    else:
        logger.info('Successfully compiled Phantom')
        logger.info(f'See "{build_log.name}" in Phantom build directory for output')

    build_log = _path / 'build' / 'build_output.log'
    with open(build_log, 'a') as fp:
        process = subprocess.Popen(
            make_command + ['setup'],
            cwd=_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            fp.write(line)
        process.communicate()[0]

    if process.returncode != 0:
        msg = 'Phantomsetup failed to compile'
        logger.error(msg)
        logger.info(f'See "{build_log.name}" in Phantom build directory for output')
        raise CompileError(msg)
    else:
        logger.info('Successfully compiled Phantomsetup')
        logger.info(f'See "{build_log.name}" in Phantom build directory for output')

    return True


def setup_calculation(
    prefix: str,
    setup_file: Union[Path, str],
    in_file: Union[Path, str],
    run_path: Union[Path, str],
    phantom_path: Union[Path, str],
) -> bool:
    """Set up Phantom calculation.

    Parameters
    ----------
    prefix
        Calculation prefix, i.e. name. E.g. if prefix is 'disc' then
        Phantom snapshots will be names disc_00000.h5, etc.
    setup_file
        The path to the Phantom prefix.setup file.
    in_file
        The path to the Phantom prefix.in file.
    run_path
        The path to the directory in which Phantom will output data.
    phantom_path
        The path to the Phantom repository.

    Returns
    -------
    bool
        Success or fail as boolean.

    Notes
    -----
    The parameters prefix, setup_file, and in_file must be consistently
    named.
    """
    _run_path = _resolved_path(run_path)
    _setup_file = _resolved_path(setup_file)
    _in_file = _resolved_path(in_file)
    _phantom_path = _resolved_path(phantom_path)
    logger.info('Setting up Phantom calculation')

    if not _run_path.exists():
        _run_path.mkdir(parents=True)

    for file in ['phantom', 'phantomsetup', 'phantom_version']:
        shutil.copy(_phantom_path / 'bin' / file, _run_path)

    shutil.copy(_setup_file, _run_path)
    shutil.copy(_in_file, _run_path)

    with open(_run_path / f'{prefix}00.log', mode='w') as f:
        process = subprocess.Popen(
            ['./phantomsetup', prefix],
            cwd=_run_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        assert process.stdout is not None
        for line in process.stdout:
            sys.stdout.write(line)
            f.write(line)
        process.communicate()[0]

    if process.returncode != 0:
        msg = 'Phantom failed to set up calculation'
        logger.error(msg)
        raise SetupError(msg)
    else:
        logger.info('Successfully set up Phantom calculation')
        logger.info(f'run_path: {run_path}')

    shutil.copy(_in_file, _run_path)

    return True


def schedule_job(run_path: Union[Path, str], job_file: Union[Path, str]):
    """Schedule the calculation with Slurm.

    Parameters
    ----------
    run_path
        The path to the directory in which Phantom will output data.
    job_file
        The path to the Slurm batch script file.

    Returns
    -------
    bool
        Success or fail as boolean.
    """
    shutil.copy(job_file, run_path)
    try:
        subprocess.run(['sbatch', job_file], cwd=run_path, check=True)
    except FileNotFoundError:
        msg = 'sbatch not available'
        logger.error(msg)
        raise ScheduleError(msg)
    except subprocess.CalledProcessError:
        msg = 'Scheduling failed'
        logger.error(msg)
        raise ScheduleError(msg)

    return True


def build_and_setup(
    *,
    prefix: str,
    setup_file: Union[Path, str],
    in_file: Union[Path, str],
    run_path: Union[Path, str],
    job_script: Union[Path, str] = None,
    phantom_path: Union[Path, str],
    phantom_version: str = None,
    phantom_patches: List[Union[Path, str]] = None,
    phantom_setup: str,
    phantom_system: str,
    phantom_extra_options: Dict[str, str],
    hdf5_path: Union[Path, str] = None,
):
    """Build Phantom and setup run.

    Get a copy of Phantom, checkout a required version, apply patches,
    and compile. Then run phantomsetup to set up the calculation, and
    optionally submit the run as a job in Slurm.

    Parameters
    ----------
    prefix
        Calculation prefix, i.e. name. E.g. if prefix is 'disc' then
        Phantom snapshots will be names disc_00000.h5, etc.
    run_path
        The path to the directory in which Phantom will output data.
    setup_file
        The path to the Phantom prefix.setup file.
    in_file
        The path to the Phantom prefix.in file.
    job_script
        The path to the Slurm batch script file, if required.
    phantom_path
        The path to the Phantom repository.
    phantom_version
        The required Phantom git commit hash, if required.
    phantom_patches
        A list of paths to patch files, if required.
    phantom_setup
        The Phantom setup, e.g. 'disc', 'dustybox', etc.
    phantom_system
        The compiler as specified in the Phantom makefile, e.g.
        'gfortran' or 'ifort'.
    phantom_extra_options
        Extra options to pass to make. This values in this dictionary
        should be strings only.
    hdf5_path
        The path to the HDF5 installation, or if None, do not compile
        with HDF5.

    Returns
    -------
    bool
        Success or fail as boolean.
    """
    # Get Phantom
    get_phantom(path=phantom_path)

    # Checkout required version (if required)
    if phantom_version is not None:
        checkout_phantom_version(path=phantom_path, version=phantom_version)

    # Apply patches (if required)
    if phantom_patches is not None:
        for patch in phantom_patches:
            patch_phantom(path=phantom_path, patch=patch)

    # Compile Phantom
    build_phantom(
        path=phantom_path,
        setup=phantom_setup,
        system=phantom_system,
        hdf5_path=hdf5_path,
        extra_options=phantom_extra_options,
    )

    # Set up calculation
    setup_calculation(
        prefix=prefix,
        setup_file=setup_file,
        in_file=in_file,
        run_path=run_path,
        phantom_path=phantom_path,
    )

    # Schedule calculation
    if job_script is not None:
        schedule_job(run_path=run_path, job_file=job_script)

    return True


def read_config(filename: Union[Path, str]) -> List[Dict[str, Any]]:
    """Read a phantombuild config file.

    Read a phantombuild config file and return a list of dictionaries
    with keyword arguments to pass to build_and_setup.

    Parameters
    ----------
    filename
        The name of the config file, as a string or Path.

    Returns
    -------
    list of dict
        One dictionary of build_and_setup keyword arguments per run.

    Examples
    --------
    Read a config file and set up runs.

    >>> runs = read_config('path_to_config_file.toml')
    >>> for run in runs:
    ...     build_and_setup(**run)
    """
    _filename = _resolved_path(filename)
    with open(_filename, mode='r') as fp:
        data = tomlkit.loads(fp.read())

    phantom_keys = ('path', 'setup', 'system', 'version', 'patches')
    run_keys = ('prefix', 'setup_file', 'in_file', 'job_script')

    kwargs_list = list()

    _kwargs = {f'phantom_{key}': data['phantom'].get(key) for key in phantom_keys}
    _kwargs['hdf5_path'] = data['phantom'].get('hdf5_path')
    _kwargs['phantom_extra_options'] = {
        item.split('=')[0]: item.split('=')[1]
        for item in data['phantom'].get('extra_make_flags')
    }

    for run in data['runs']:
        kwargs = copy.copy(_kwargs)
        kwargs['run_path'] = run['path']
        for key in run_keys:
            kwargs[key] = run[key]
        kwargs_list.append(kwargs)

    return kwargs_list


def write_config(filename: Union[Path, str]):
    """Write a phantombuild config file template.

    Parameters
    ----------
    filename
        The name of the config file, as a string or Path.
    """
    _filename = _resolved_path(filename)
    shutil.copy(Path(__file__).parent / 'template.toml', _filename)


def _resolved_path(inp: Union[str, Path]) -> Path:
    return pathlib.Path(inp).expanduser().resolve()
