import pathlib
import subprocess


class PatchError(Exception):
    pass


class CompileError(Exception):
    pass


def get_phantom(phantom_dir: pathlib.Path):
    """
    Get Phantom repository.

    Parameters
    ----------
    phantom_dir : pathlib.Path
        The path to the Phantom repository.
    """

    print('>>> Getting Phantom <<<')

    if not phantom_dir.exists():
        print('Cloning fresh copy of Phantom')
        subprocess.check_output(
            ['git', 'clone', 'git@bitbucket.org:danielprice/phantom', phantom_dir.stem],
            cwd=phantom_dir.parent,
        )
    else:
        if not (
            subprocess.check_output(
                ['git', 'config', '--local', '--get', 'remote.origin.url'],
                cwd=phantom_dir,
            )
            .strip()
            .decode()
            == 'git@bitbucket.org:danielprice/phantom'
        ):
            raise ValueError('phantom_dir is not Phantom')
        else:
            print('Phantom already cloned')


def check_phantom_version(
    phantom_dir: pathlib.Path,
    required_phantom_git_sha: str,
    phantom_patch: pathlib.Path,
):
    """
    Check Phantom version, and apply patches if required.

    Parameters
    ----------
    phantom_dir : pathlib.Path
        The path to the Phantom repository.

    required_phantom_git_sha : str
        The required Phantom git SHA.

    phantom_patch : pathlib.Path
        The path to the patch file, if required.
    """

    print('>>> Checking Phantom version <<<')

    # Check git commit SHA
    phantom_git_sha = (
        subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=phantom_dir)
        .strip()
        .decode()
    )
    if phantom_git_sha != required_phantom_git_sha:
        print(f'Checking out Phantom version: {required_phantom_git_sha}')
        subprocess.check_output(
            ['git', 'checkout', required_phantom_git_sha], cwd=phantom_dir
        )
    else:
        print('Required version of Phantom already checked out')

    # Check if clean
    git_status = (
        subprocess.check_output(['git', 'status', '--porcelain'], cwd=phantom_dir)
        .strip()
        .decode()
    )
    if not git_status == '':
        if phantom_patch is None:
            print('Cleaning repository')
        else:
            print('Cleaning repository to apply patches')
        subprocess.run(['git', 'reset', 'HEAD'], cwd=phantom_dir)
        subprocess.run(['git', 'clean', '--force'], cwd=phantom_dir)
        subprocess.run(['git', 'restore', '--', '*'], cwd=phantom_dir)

    # Apply patch
    if phantom_patch is not None:
        print('Applying patch to Phantom')
        subprocess.check_output(['git', 'apply', phantom_patch], cwd=phantom_dir)


def build_phantom(
    phantom_dir: pathlib.Path,
    setup: str,
    system: str,
    hdf5_location: pathlib.Path,
    extra_makefile_options: dict,
):
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
        The path to the HDF5 installation.

    extra_makefile_options : dict
        Extra options to pass to make. This values in this dictionary
        should be strings only.
    """

    print('>>> Building Phantom <<<')

    if not hdf5_location.exists():
        raise FileNotFoundError('Cannot determine HDF5 library location')

    make_command = [
        'make',
        'SETUP=' + setup,
        'SYSTEM=' + system,
        'HDF5=yes',
        'HDF5ROOT=' + str(hdf5_location),
        'phantom',
        'setup',
    ]

    if extra_makefile_options is not None:
        make_command += [key + '=' + val for key, val in extra_makefile_options.items()]

    with open(phantom_dir / 'build' / 'build-output.log', 'w') as fp:
        result = subprocess.run(make_command, cwd=phantom_dir, stdout=fp, stderr=fp)

    if result.returncode != 0:
        raise CompileError('Phantom failed compiling')

    print('Phantom successfully built. See "build-output.log" in Phantom build dir.')
