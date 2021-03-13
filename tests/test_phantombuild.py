"""Testing phantombuild."""

import tempfile
from pathlib import Path

import pytest

import phantombuild as pb
from phantombuild.phantombuild import (
    CompileError,
    HDF5LibraryNotFound,
    PatchError,
    RepoError,
)

VERSION = '3252f52501cac9565f9bc40527346c0e224757b9'


def test_get_phantom():
    """Test getting Phantom from GitHub."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / 'phantom'
        pb.get_phantom(path)
        pb.get_phantom(path)
        (path / '.git/config').unlink()
        with pytest.raises(RepoError):
            pb.get_phantom(path)


def test_checkout_phantom_version_clean():
    """Test checking out a Phantom version."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / 'phantom'
        pb.get_phantom(path)
        pb.checkout_phantom_version(path=path, version=VERSION)
        pb.checkout_phantom_version(path=path, version=VERSION)


def test_checkout_phantom_version_dirty():
    """Test checking out a Phantom version."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / 'phantom'
        pb.get_phantom(path)
        (path / 'src/main/phantom.F90').unlink()
        pb.checkout_phantom_version(path=path, version=VERSION)


def test_phantom_patch():
    """Test patching Phantom."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / 'phantom'
        pb.get_phantom(path)
        pb.checkout_phantom_version(path=path, version=VERSION)
        patch = Path(__file__).parent / 'stub' / 'test.patch'
        pb.patch_phantom(path=path, patch=patch)
        kwargs = {'path': path, 'patch': patch}
        with pytest.raises(PatchError):
            pb.patch_phantom(**kwargs)


def test_build_phantom():
    """Test building Phantom."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        path = Path(tmpdirname) / 'phantom'
        hdf5_path = Path('non_existent_dir')
        pb.get_phantom(path)
        pb.build_phantom(
            path=path,
            setup='empty',
            system='gfortran',
            extra_options={'MAXP': '1000000'},
        )
        kwargs = {
            'path': path,
            'setup': 'empty',
            'system': 'gfortran',
            'hdf5_path': hdf5_path,
        }
        with pytest.raises(HDF5LibraryNotFound):
            pb.build_phantom(**kwargs)
        kwargs = {
            'path': path,
            'setup': 'FakeSetup',
            'system': 'gfortran',
        }
        with pytest.raises(CompileError):
            pb.build_phantom(**kwargs)


def test_setup_calculation():
    """Test setting up Phantom calculation."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        phantom_path = Path(tmpdirname) / 'phantom'
        run_path = Path(tmpdirname) / 'run_path'
        input_dir = Path(__file__).parent / 'stub'
        in_file = input_dir / 'disc.in'
        setup_file = input_dir / 'disc.setup'
        pb.get_phantom(phantom_path)
        pb.build_phantom(
            path=phantom_path, version=VERSION, setup='disc', system='gfortran'
        )
        pb.setup_calculation(
            prefix='disc',
            setup_file=setup_file,
            in_file=in_file,
            run_path=run_path,
            phantom_path=phantom_path,
        )
