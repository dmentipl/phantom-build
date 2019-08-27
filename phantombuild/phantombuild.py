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

    print('')
    print('------------------------------------------------------------------------')
    print('>>> Getting Phantom <<<')
    print('------------------------------------------------------------------------')
    print('')

    if not phantom_dir.exists():
        print('Cloning fresh copy of Phantom')
        subprocess.run(
            [
                'git',
                'clone',
                'https://bitbucket.org/danielprice/phantom.git',
                phantom_dir.stem,
            ],
            cwd=phantom_dir.parent,
            stdout=subprocess.PIPE,
        )
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
                'https://bitbucket.org/danielprice/phantom.git',
            ]
        ):
            raise ValueError('phantom_dir is not Phantom')
        else:
            print('Phantom already cloned')


def checkout_phantom_version(
    phantom_dir: pathlib.Path, required_phantom_git_commit_hash: str
):
    """
    Check out a particular Phantom version.

    Parameters
    ----------
    phantom_dir : pathlib.Path
        The path to the Phantom repository.

    required_phantom_git_commit_hash : str
        The required Phantom git commit hash.
    """

    print('')
    print('------------------------------------------------------------------------')
    print('>>> Checking Phantom version <<<')
    print('------------------------------------------------------------------------')
    print('')

    # Check git commit hash
    phantom_git_commit_hash = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], cwd=phantom_dir, stdout=subprocess.PIPE, text=True
    ).stdout.strip()
    if phantom_git_commit_hash != required_phantom_git_commit_hash:
        print(f'Checking out Phantom version: {required_phantom_git_commit_hash}')
        subprocess.run(
            ['git', 'checkout', required_phantom_git_commit_hash],
            cwd=phantom_dir,
            stdout=subprocess.PIPE,
        )
    else:
        print('Required version of Phantom already checked out')

    # Check if clean
    git_status = subprocess.run(
        ['git', 'status', '--porcelain'],
        cwd=phantom_dir,
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    if not git_status == '':
        print('Cleaning repository')
        subprocess.run(['git', 'reset', 'HEAD'], cwd=phantom_dir, stout=subprocess.PIPE)
        subprocess.run(
            ['git', 'clean', '--force'], cwd=phantom_dir, stout=subprocess.PIPE
        )
        subprocess.run(
            ['git', 'restore', '--', '*'], cwd=phantom_dir, stout=subprocess.PIPE
        )


def patch_phantom(phantom_dir: pathlib.Path, phantom_patch: pathlib.Path):
    """
    Apply patch to Phantom.

    Parameters
    ----------
    phantom_dir : pathlib.Path
        The path to the Phantom repository.

    phantom_patch : pathlib.Path
        The path to the patch file, if required.
    """

    print('')
    print('------------------------------------------------------------------------')
    print('>>> Applying patch to Phantom <<<')
    print('------------------------------------------------------------------------')
    print('')

    result = subprocess.run(
        ['git', 'apply', phantom_patch], cwd=phantom_dir, stdout=subprocess.PIPE
    )
    if result.returncode != 0:
        raise PatchError('Cannot patch Phantom')


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
        The path to the HDF5 installation, or if None, do not compile
        with HDF5.

    extra_makefile_options : dict
        Extra options to pass to make. This values in this dictionary
        should be strings only.
    """

    print('')
    print('------------------------------------------------------------------------')
    print('>>> Building Phantom <<<')
    print('------------------------------------------------------------------------')
    print('')

    make_command = ['make', 'SETUP=' + setup, 'SYSTEM=' + system, 'phantom', 'setup']

    if hdf5_location is not None:
        if not hdf5_location.exists():
            raise FileNotFoundError('Cannot determine HDF5 library location')
        make_command += ['HDF5=yes', 'HDF5ROOT=' + str(hdf5_location.resolve())]

    if extra_makefile_options is not None:
        make_command += [key + '=' + val for key, val in extra_makefile_options.items()]

    with open(phantom_dir / 'build' / 'build-output.log', 'w') as fp:
        result = subprocess.run(make_command, cwd=phantom_dir, stdout=fp, stderr=fp)

    if result.returncode != 0:
        raise CompileError('Phantom failed compiling')

    print('Phantom successfully built. See "build-output.log" in Phantom build dir.')
