import logging
import pathlib
import subprocess
from typing import Dict


class RepoError(Exception):
    """Exception for dealing with Phantom git repository."""


class PatchError(Exception):
    """Exception for dealing with patching Phantom."""


class CompileError(Exception):
    """Exception for dealing with compiling Phantom."""


class HDF5LibraryNotFound(Exception):
    """Cannot find HDF5 library."""


def setup_logger(filename: pathlib.Path = None) -> logging.Logger:

    if filename is None:
        filename = pathlib.Path('phantom-build.log')

    logger = logging.getLogger('phantom-build')

    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(filename, mode='w')

    console_format = logging.Formatter('%(name)s %(levelname)s: %(message)s')
    file_format = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    file_handler.setFormatter(file_format)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.setLevel(logging.INFO)

    return logger


LOGGER = setup_logger()


def get_phantom(phantom_dir: pathlib.Path) -> bool:
    """
    Get Phantom repository.

    Parameters
    ----------
    phantom_dir : pathlib.Path
        The path to the Phantom repository.

    Returns
    -------
    bool
        Success or fail as boolean.
    """

    LOGGER.info('')
    LOGGER.info('------------------------------------------------')
    LOGGER.info('>>> Getting Phantom')
    LOGGER.info('------------------------------------------------')

    if not phantom_dir.exists():
        LOGGER.info('Cloning fresh copy of Phantom')
        LOGGER.info(f'phantom_dir: {_nice_path(phantom_dir)}')
        result = subprocess.run(
            [
                'git',
                'clone',
                'https://bitbucket.org/danielprice/phantom.git',
                phantom_dir.stem,
            ],
            cwd=phantom_dir.parent,
        )
        if result.returncode != 0:
            LOGGER.info('Phantom clone failed')
            raise RepoError('Fail to close repo')
        else:
            LOGGER.info('Phantom successfully cloned')
    else:
        if not (
            subprocess.run(
                ['git', 'config', '--local', '--get', 'remote.origin.url'],
                cwd=phantom_dir,
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
            LOGGER.info('phantom_dir is not Phantom')
            raise RepoError('phantom_dir is not Phantom')
        else:
            LOGGER.info('Phantom already cloned')
            LOGGER.info(f'phantom_dir: {_nice_path(phantom_dir)}')

    return True


def checkout_phantom_version(
    phantom_dir: pathlib.Path, required_phantom_git_commit_hash: str
) -> bool:
    """
    Check out a particular Phantom version.

    Parameters
    ----------
    phantom_dir : pathlib.Path
        The path to the Phantom repository.

    required_phantom_git_commit_hash : str
        The required Phantom git commit hash.

    Returns
    -------
    bool
        Success or fail as boolean.
    """

    LOGGER.info('')
    LOGGER.info('------------------------------------------------')
    LOGGER.info('>>> Checking out required Phantom version')
    LOGGER.info('------------------------------------------------')

    # Check git commit hash
    phantom_git_commit_hash = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], cwd=phantom_dir, stdout=subprocess.PIPE, text=True
    ).stdout.strip()
    short_hash = subprocess.run(
        ['git', 'rev-parse', '--short', required_phantom_git_commit_hash],
        cwd=phantom_dir,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    if phantom_git_commit_hash != required_phantom_git_commit_hash:
        LOGGER.info('Checking out required Phantom version')
        LOGGER.info(f'Git commit hash: {short_hash}')
        result = subprocess.run(
            ['git', 'checkout', required_phantom_git_commit_hash], cwd=phantom_dir
        )
        if result.returncode != 0:
            LOGGER.info('Failed to checkout required version')
            raise RepoError('Failed to checkout required version')
        else:
            LOGGER.info('Successfully checked out required version')
    else:
        LOGGER.info('Required version of Phantom already checked out')
        LOGGER.info(f'Git commit hash: {short_hash}')

    # Check if clean
    git_status = subprocess.run(
        ['git', 'status', '--porcelain'],
        cwd=phantom_dir,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    if not git_status == '':
        LOGGER.info('Cleaning repository')
        results = list()
        results.append(subprocess.run(['git', 'reset', 'HEAD'], cwd=phantom_dir))
        results.append(subprocess.run(['git', 'clean', '--force'], cwd=phantom_dir))
        results.append(subprocess.run(['git', 'checkout', '--', '*'], cwd=phantom_dir))
        if any(result.returncode != 0 for result in results):
            LOGGER.info('Failed to clean repo')
            raise RepoError('Failed to clean repo')
        else:
            LOGGER.info('Successfully cleaned repo')

    return True


def patch_phantom(phantom_dir: pathlib.Path, phantom_patch: pathlib.Path) -> bool:
    """
    Apply patch to Phantom.

    Parameters
    ----------
    phantom_dir : pathlib.Path
        The path to the Phantom repository.

    phantom_patch : pathlib.Path
        The path to the patch file, if required.

    Returns
    -------
    bool
        Success or fail as boolean.
    """

    LOGGER.info('')
    LOGGER.info('------------------------------------------------')
    LOGGER.info('>>> Applying patch to Phantom')
    LOGGER.info('------------------------------------------------')

    LOGGER.info(f'Patch file: {_nice_path(phantom_patch)}')

    result = subprocess.run(['git', 'apply', phantom_patch], cwd=phantom_dir)
    if result.returncode != 0:
        LOGGER.error('Failed to patch Phantom')
        raise PatchError('Fail to patch Phantom')
    else:
        LOGGER.info('Successfully patched Phantom')

    return True


def build_phantom(
    *,
    phantom_dir: pathlib.Path,
    setup: str,
    system: str,
    hdf5_location: pathlib.Path = None,
    extra_makefile_options: Dict[str, str] = None,
) -> bool:
    """
    Build Phantom.

    Parameters
    ----------
    phantom_dir : pathlib.Path
        The path to the Phantom repository.

    setup : str
        The Phantom setup, e.g. 'disc', 'dustybox', etc.

    system : str
        The compiler as specified in the Phantom makefile, e.g.
        'gfortran' or 'ifort'.

    hdf5_location : pathlib.Path
        The path to the HDF5 installation, or if None, do not compile
        with HDF5.

    extra_makefile_options : dict
        Extra options to pass to make. This values in this dictionary
        should be strings only.

    Returns
    -------
    bool
        Success or fail as boolean.
    """

    LOGGER.info('')
    LOGGER.info('------------------------------------------------')
    LOGGER.info('>>> Building Phantom')
    LOGGER.info('------------------------------------------------')

    make_command = ['make', 'SETUP=' + setup, 'SYSTEM=' + system, 'phantom', 'setup']

    if hdf5_location is not None:
        if not hdf5_location.exists():
            raise HDF5LibraryNotFound('Cannot determine HDF5 library location')
        make_command += ['HDF5=yes', 'HDF5ROOT=' + str(hdf5_location.resolve())]

    if extra_makefile_options is not None:
        make_command += [key + '=' + val for key, val in extra_makefile_options.items()]

    build_log = phantom_dir / 'build' / 'build_output.log'
    with open(build_log, 'w') as fp:
        result = subprocess.run(make_command, cwd=phantom_dir, stdout=fp, stderr=fp)

    if result.returncode != 0:
        LOGGER.info('Phantom failed to compile')
        raise CompileError('Phantom failed to compile')
    else:
        LOGGER.info('Successfully compiled Phantom')
        LOGGER.info(f'See "{build_log.name}" in Phantom build dir')

    return True


def _nice_path(path: pathlib.Path) -> str:
    """
    Convert absolute path to a string relative to '~', i.e. $HOME.

    E.g. '/Users/user/dir/file.txt' is converted to '~/dir/file.txt'.

    Parameters
    ----------
    path : pathlib.Path
        The path to convert.

    Returns
    -------
    str
        The converted path.
    """
    try:
        return '~' + str(path.relative_to(pathlib.Path.home()))
    except ValueError:
        return './' + str(path)
