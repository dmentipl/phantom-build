"""Phantom build."""

import logging
import os
import pathlib
import shutil
import subprocess
import sys
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List, Union

import tomlkit
from jinja2 import Template

REPO_URL = 'https://github.com/danieljprice/phantom.git'
GIT_URLS = [
    'git@github.com:danieljprice/phantom',
    'git@github.com:danieljprice/phantom.git',
    'https://github.com/danieljprice/phantom',
    'https://github.com/danieljprice/phantom.git',
]


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

    Raises
    ------
    RepoError
        If the repository can not be cloned.
    """
    _path = _resolved_path(path)
    logger.info('Getting Phantom repository')
    logger.info(f'path: {_path}')

    if not _path.exists():
        logger.info('Cloning fresh copy of Phantom')
        result = subprocess.run(
            ['git', 'clone', REPO_URL, _path.stem], cwd=_path.parent,
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
            in GIT_URLS
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

    Raises
    ------
    RepoError
        If the required version cannot be checked out.
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
    logger.info(f'Git commit hash: {short_hash}')
    if phantom_git_commit_hash != version:
        logger.info('Checking out required Phantom version')
        result = subprocess.run(['git', 'checkout', version], cwd=_path)
        if result.returncode != 0:
            msg = 'Failed to checkout required version'
            logger.error(msg)
            raise RepoError(msg)
        else:
            logger.info('Successfully checked out required version')
    else:
        logger.info('Required version of Phantom already checked out')

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

    Raises
    ------
    PatchError
        If the patch cannot be applied.
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
    *,
    path: Union[Path, str],
    version: str = None,
    patches: List[Union[Path, str]] = None,
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
    version
        The required Phantom version specified by git commit hash.
    patches
        A list of paths to patch files, if required.
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

    Raises
    ------
    CompileError
        If phantom or phantomsetup cannot be compiled.
    HDF5LibraryNotFound
        If the HDF5 library cannot be located.
    """
    _path = _resolved_path(path)

    # Get Phantom
    get_phantom(path=_path)

    # Checkout required version (if required)
    if version is not None:
        checkout_phantom_version(path=_path, version=version)

    # Apply patches (if required)
    if patches is not None:
        for patch in patches:
            _patch = _resolved_path(patch)
            patch_phantom(path=_path, patch=_patch)

    logger.info('Building Phantom')
    logger.info(f'setup: {setup}')
    logger.info(f'system: {system}')
    if hdf5_path is not None:
        logger.info(f'hdf5_path: {hdf5_path}')
    if extra_options is not None:
        logger.info(f'extra_options: {extra_options}')

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


def schedule_job(run_path: Union[Path, str], job_script: Union[Path, str]):
    """Schedule the calculation with Slurm.

    Parameters
    ----------
    run_path
        The path to the directory in which Phantom will output data.
    job_script
        The path to the Slurm batch script file.

    Returns
    -------
    bool
        Success or fail as boolean.

    Raises
    ------
    ScheduleError
        If the run cannot be scheduled.
    """
    logger.info('Scheduling job with Slurm')
    _run_path = _resolved_path(run_path)
    _job_script = _resolved_path(job_script)
    shutil.copy(_job_script, _run_path)
    try:
        subprocess.run(['sbatch', _job_script], cwd=_run_path, check=True)
        logger.info('Scheduled job successfully')
    except FileNotFoundError:
        msg = 'sbatch not available'
        logger.error(msg)
        raise ScheduleError(msg)
    except subprocess.CalledProcessError:
        msg = 'Scheduling failed'
        logger.error(msg)
        raise ScheduleError(msg)

    return True


def setup_calculation(
    *,
    prefix: str,
    setup_file: Union[Path, str],
    in_file: Union[Path, str],
    run_path: Union[Path, str],
    phantom_path: Union[Path, str],
    job_script: Union[Path, str] = None,
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
    job_script
        The path to the Slurm batch script file, if required.

    Returns
    -------
    bool
        Success or fail as boolean.

    Raises
    ------
    SetupError
        If the run cannot be set up.

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
    logger.info(f'prefix: {prefix}')
    logger.info(f'setup_file: {_setup_file}')
    logger.info(f'in_file: {_in_file}')
    logger.info(f'run_path: {_run_path}')

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

    shutil.copy(_in_file, _run_path)

    # Schedule calculation (if required)
    if job_script is not None:
        schedule_job(run_path=_run_path, job_script=job_script)

    return True


def read_config(filename: Union[Path, str]) -> Dict[str, Any]:
    """Read a phantombuild config file.

    Parameters
    ----------
    filename
        The name of the config file, as a string or Path.

    Returns
    -------
    dict
        The dictionary contains a dictionary of phantom build options,
        and a list of dictionaries of run setup options:
            {
                'phantom': ...,
                'runs': [
                    ...,
                    ...,
                ]
            }
        The 'runs' list may be empty.

    Examples
    --------
    Read a config file and set up multiple runs.

    >>> config = read_config('path_to_config_file.toml')
    >>> build_phantom(**config['phantom'])
    >>> phantom_path = config['phantom']['path']
    >>> for run in config['runs']:
    ...     run_path = run.pop('path')
    ...     setup_calculation(run_path=run_path, phantom_path=phantom_path, **run)
    """
    _filename = _resolved_path(filename)
    logger.info('Reading config file')
    logger.info(f'config: {_filename}')

    with open(_filename, mode='r') as fp:
        file = fp.read()

    template = Template(file)
    data = tomlkit.loads(template.render(env=os.environ))

    phantom_keys = ('path', 'setup', 'system', 'version', 'patches', 'hdf5_path')
    run_keys = ('path', 'prefix', 'setup_file', 'in_file', 'job_script')

    config: Dict[str, Any] = dict()

    d = {key: data['phantom'].get(key) for key in phantom_keys}
    d['extra_options'] = {
        item.split('=')[0]: item.split('=')[1]
        for item in data['phantom'].get('extra_options', [])
    }
    config['phantom'] = d

    runs = data.get('runs')
    if runs is None:
        logger.info('Successfully read config file')
        return config

    l = list()
    for run in runs:
        d = dict()
        for key in run_keys:
            d[key] = run.get(key)
        l.append(d)
    config['runs'] = l

    logger.info('Successfully read config file')
    return config


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
