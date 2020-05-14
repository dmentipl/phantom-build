"""Phantom build."""

import logging
import pathlib
import shutil
import subprocess
import sys
from logging import Logger
from pathlib import Path
from typing import Dict, Union


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


def get_phantom(phantom_dir: Path) -> bool:
    """Get Phantom repository.

    Parameters
    ----------
    phantom_dir
        The path to the Phantom repository.

    Returns
    -------
    bool
        Success or fail as boolean.
    """
    _phantom_dir = _resolved_path(phantom_dir)
    logger.info('Getting Phantom repository')
    logger.info(f'phantom_dir: {_nice_path(_phantom_dir)}')

    if not _phantom_dir.exists():
        logger.info('Cloning fresh copy of Phantom')
        result = subprocess.run(
            [
                'git',
                'clone',
                'https://bitbucket.org/danielprice/phantom.git',
                _phantom_dir.stem,
            ],
            cwd=_phantom_dir.parent,
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
                cwd=_phantom_dir,
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
            msg = 'phantom_dir is not Phantom'
            logger.error(msg)
            raise RepoError(msg)
        else:
            logger.info('Phantom already cloned')

    return True


def checkout_phantom_version(
    *, phantom_dir: Path, required_phantom_git_commit_hash: str
) -> bool:
    """Check out a particular Phantom version.

    Parameters
    ----------
    phantom_dir
        The path to the Phantom repository.
    required_phantom_git_commit_hash
        The required Phantom git commit hash.

    Returns
    -------
    bool
        Success or fail as boolean.
    """
    _phantom_dir = _resolved_path(phantom_dir)
    logger.info('Getting required Phantom version')

    # Check git commit hash
    phantom_git_commit_hash = subprocess.run(
        ['git', 'rev-parse', 'HEAD'],
        cwd=_phantom_dir,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    short_hash = subprocess.run(
        ['git', 'rev-parse', '--short', required_phantom_git_commit_hash],
        cwd=_phantom_dir,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    if phantom_git_commit_hash != required_phantom_git_commit_hash:
        logger.info('Checking out required Phantom version')
        logger.info(f'Git commit hash: {short_hash}')
        result = subprocess.run(
            ['git', 'checkout', required_phantom_git_commit_hash], cwd=_phantom_dir
        )
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
        ['git', 'status', '--porcelain'],
        cwd=_phantom_dir,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    if not git_status == '':
        logger.info('Cleaning repository')
        results = list()
        results.append(subprocess.run(['git', 'reset', 'HEAD'], cwd=_phantom_dir))
        results.append(subprocess.run(['git', 'clean', '--force'], cwd=_phantom_dir))
        results.append(subprocess.run(['git', 'checkout', '--', '*'], cwd=_phantom_dir))
        if any(result.returncode != 0 for result in results):
            msg = 'Failed to clean repo'
            logger.error(msg)
            raise RepoError(msg)
        else:
            logger.info('Successfully cleaned repo')

    return True


def patch_phantom(*, phantom_dir: Path, phantom_patch: Path) -> bool:
    """Apply patch to Phantom.

    Parameters
    ----------
    phantom_dir
        The path to the Phantom repository.
    phantom_patch
        The path to the patch file, if required.

    Returns
    -------
    bool
        Success or fail as boolean.
    """
    _phantom_dir = _resolved_path(phantom_dir)
    _phantom_patch = _resolved_path(phantom_patch)

    logger.info('Patching Phantom')
    logger.info(f'Patch file: {_nice_path(_phantom_patch)}')

    result = subprocess.run(['git', 'apply', _phantom_patch], cwd=_phantom_dir)
    if result.returncode != 0:
        msg = 'Failed to patch Phantom'
        logger.error(msg)
        raise PatchError(msg)
    else:
        logger.info('Successfully patched Phantom')

    return True


def build_phantom(
    *,
    phantom_dir: Path,
    setup: str,
    system: str,
    hdf5_location: Path = None,
    extra_makefile_options: Dict[str, str] = None,
) -> bool:
    """Build Phantom.

    Parameters
    ----------
    phantom_dir
        The path to the Phantom repository.
    setup
        The Phantom setup, e.g. 'disc', 'dustybox', etc.
    system
        The compiler as specified in the Phantom makefile, e.g.
        'gfortran' or 'ifort'.
    hdf5_location
        The path to the HDF5 installation, or if None, do not compile
        with HDF5.
    extra_makefile_options
        Extra options to pass to make. This values in this dictionary
        should be strings only.

    Returns
    -------
    bool
        Success or fail as boolean.
    """
    _phantom_dir = _resolved_path(phantom_dir)
    logger.info('Building Phantom')

    make_command = ['make', 'SETUP=' + setup, 'SYSTEM=' + system]

    if hdf5_location is not None:
        _hdf5_location = _resolved_path(hdf5_location)
        if not _hdf5_location.exists():
            raise HDF5LibraryNotFound('Cannot determine HDF5 library location')
        make_command += ['HDF5=yes', 'HDF5ROOT=' + str(_hdf5_location.resolve())]

    if extra_makefile_options is not None:
        make_command += [key + '=' + val for key, val in extra_makefile_options.items()]

    build_log = _phantom_dir / 'build' / 'build_output.log'
    with open(build_log, 'w') as fp:
        result = subprocess.run(make_command, cwd=_phantom_dir, stdout=fp, stderr=fp)

    if result.returncode != 0:
        msg = 'Phantom failed to compile'
        logger.error(msg)
        logger.info(f'See "{build_log.name}" in Phantom build dir for output')
        raise CompileError(msg)
    else:
        logger.info('Successfully compiled Phantom')
        logger.info(f'See "{build_log.name}" in Phantom build dir for output')

    build_log = _phantom_dir / 'build' / 'build_output.log'
    with open(build_log, 'a') as fp:
        result = subprocess.run(
            make_command + ['setup'], cwd=_phantom_dir, stdout=fp, stderr=fp
        )

    if result.returncode != 0:
        msg = 'Phantomsetup failed to compile'
        logger.error(msg)
        logger.info(f'See "{build_log.name}" in Phantom build dir for output')
        raise CompileError(msg)
    else:
        logger.info('Successfully compiled Phantomsetup')
        logger.info(f'See "{build_log.name}" in Phantom build dir for output')

    return True


def setup_calculation(
    *, prefix: str, run_dir: Path, input_dir: Path, phantom_dir: Path
) -> bool:
    """Set up Phantom calculation.

    Parameters
    ----------
    prefix
        Calculation prefix, i.e. name. E.g. if prefix is 'disc' then
        Phantom snapshots will be names disc_00000.h5, etc.
    run_dir
        The path to the directory in which Phantom will output data.
    input_dir
        The path to the directory containing Phantom prefix.setup and
        prefix.in files. These files must have names corresponding to
        the prefix.
    phantom_dir
        The path to the Phantom repository.

    Returns
    -------
    bool
        Success or fail as boolean.
    """
    _run_dir = _resolved_path(run_dir)
    _input_dir = _resolved_path(input_dir)
    _phantom_dir = _resolved_path(phantom_dir)
    logger.info('Setting up Phantom calculation')

    if not _run_dir.exists():
        _run_dir.mkdir(parents=True)

    for file in ['phantom', 'phantomsetup', 'phantom_version']:
        shutil.copy(_phantom_dir / 'bin' / file, _run_dir)

    shutil.copy(_input_dir / f'{prefix}.setup', _run_dir)
    shutil.copy(_input_dir / f'{prefix}.in', _run_dir)

    with open(_run_dir / f'{prefix}00.log', mode='w') as f:
        process = subprocess.Popen(
            ['./phantomsetup', prefix],
            cwd=_run_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
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
        logger.info(f'run_dir: {run_dir}')

    shutil.copy(_input_dir / f'{prefix}.in', _run_dir)

    return True


def _nice_path(path: Path) -> str:
    """Convert absolute path to a string relative to '~', i.e. $HOME.

    E.g. '/Users/user/dir/file.txt' is converted to '~/dir/file.txt'.

    Parameters
    ----------
    path
        The path to convert.

    Returns
    -------
    str
        The converted path.
    """
    try:
        return '~/' + str(path.relative_to(pathlib.Path.home()))
    except ValueError:
        if path.anchor == '/':
            return str(path)
        else:
            return './' + str(path)


def _resolved_path(inp: Union[str, Path]) -> Path:
    return pathlib.Path(inp).expanduser().resolve()
