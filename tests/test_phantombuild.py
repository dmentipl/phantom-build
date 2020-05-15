"""Testing phantombuild."""

import pathlib
import tempfile

import pytest

import phantombuild as pb
from phantombuild.phantombuild import (
    CompileError,
    HDF5LibraryNotFound,
    PatchError,
    RepoError,
)


def test_get_phantom():
    """Test getting Phantom from bitbucket."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        phantom_dir = pathlib.Path(tmpdirname) / 'phantom_dir'
        pb.get_phantom(phantom_dir)
        pb.get_phantom(phantom_dir)
        (phantom_dir / '.git/config').unlink()
        with pytest.raises(RepoError):
            pb.get_phantom(phantom_dir)


def test_checkout_phantom_version_clean():
    """Test checking out a Phantom version."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        phantom_dir = pathlib.Path(tmpdirname) / 'phantom_dir'
        pb.get_phantom(phantom_dir)
        required_phantom_git_commit_hash = '6666c55feea1887b2fd8bb87fbe3c2878ba54ed7'
        pb.checkout_phantom_version(
            phantom_dir=phantom_dir,
            required_phantom_git_commit_hash=required_phantom_git_commit_hash,
        )
        pb.checkout_phantom_version(
            phantom_dir=phantom_dir,
            required_phantom_git_commit_hash=required_phantom_git_commit_hash,
        )


def test_checkout_phantom_version_dirty():
    """Test checking out a Phantom version."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        phantom_dir = pathlib.Path(tmpdirname) / 'phantom_dir'
        pb.get_phantom(phantom_dir)
        required_phantom_git_commit_hash = '6666c55feea1887b2fd8bb87fbe3c2878ba54ed7'
        (phantom_dir / 'src/main/phantom.F90').unlink()
        pb.checkout_phantom_version(
            phantom_dir=phantom_dir,
            required_phantom_git_commit_hash=required_phantom_git_commit_hash,
        )


def test_phantom_patch():
    """Test patching Phantom."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        phantom_dir = pathlib.Path(tmpdirname) / 'phantom_dir'
        pb.get_phantom(phantom_dir)
        required_phantom_git_commit_hash = '6666c55feea1887b2fd8bb87fbe3c2878ba54ed7'
        pb.checkout_phantom_version(
            phantom_dir=phantom_dir,
            required_phantom_git_commit_hash=required_phantom_git_commit_hash,
        )
        phantom_patch = pathlib.Path(__file__).parent / 'stub' / 'test.patch'
        pb.patch_phantom(phantom_dir=phantom_dir, phantom_patch=phantom_patch)
        kwargs = {'phantom_dir': phantom_dir, 'phantom_patch': phantom_patch}
        with pytest.raises(PatchError):
            pb.patch_phantom(**kwargs)


def test_build_phantom():
    """Test building Phantom."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        phantom_dir = pathlib.Path(tmpdirname) / 'phantom_dir'
        hdf5_location = pathlib.Path('non_existent_dir')
        pb.get_phantom(phantom_dir)
        pb.build_phantom(
            phantom_dir=phantom_dir,
            setup='empty',
            system='gfortran',
            extra_makefile_options={'MAXP': '1000000'},
        )
        kwargs = {
            'phantom_dir': phantom_dir,
            'setup': 'empty',
            'system': 'gfortran',
            'hdf5_location': hdf5_location,
        }
        with pytest.raises(HDF5LibraryNotFound):
            pb.build_phantom(**kwargs)
        kwargs = {
            'phantom_dir': phantom_dir,
            'setup': 'FakeSetup',
            'system': 'gfortran',
        }
        with pytest.raises(CompileError):
            pb.build_phantom(**kwargs)


@pytest.mark.skip(reason='This test fails on Travis CI; not sure why...')
def test_setup_calculation():
    """Test setting up Phantom calculation."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        phantom_dir = pathlib.Path(tmpdirname) / 'phantom_dir'
        run_dir = pathlib.Path(tmpdirname) / 'run_dir'
        input_dir = pathlib.Path(__file__).parent / 'stub'
        pb.get_phantom(phantom_dir)
        pb.build_phantom(
            phantom_dir=phantom_dir, setup='disc', system='gfortran',
        )
        pb.setup_calculation(
            prefix='disc', run_dir=run_dir, input_dir=input_dir, phantom_dir=phantom_dir
        )
