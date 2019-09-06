"""
Testing phantombuild.
"""

import pathlib
import tempfile
import unittest

import phantombuild as pb
from phantombuild.phantombuild import (
    CompileError,
    HDF5LibraryNotFound,
    PatchError,
    RepoError,
)


class TestGetPhantom(unittest.TestCase):
    """Test getting Phantom from bitbucket."""

    def test_get_phantom(self):

        with tempfile.TemporaryDirectory() as tmpdirname:
            phantom_dir = pathlib.Path(tmpdirname) / 'phantom_dir'
            pb.get_phantom(phantom_dir)
            pb.get_phantom(phantom_dir)
            (phantom_dir / '.git/config').unlink()
            self.assertRaises(RepoError, pb.get_phantom, phantom_dir)


class TestCheckoutPhantom(unittest.TestCase):
    """Test checking out a Phantom version."""

    def test_checkout_phantom_version_clean(self):

        with tempfile.TemporaryDirectory() as tmpdirname:
            phantom_dir = pathlib.Path(tmpdirname) / 'phantom_dir'
            pb.get_phantom(phantom_dir)
            required_phantom_git_commit_hash = (
                '6666c55feea1887b2fd8bb87fbe3c2878ba54ed7'
            )
            pb.checkout_phantom_version(
                phantom_dir=phantom_dir,
                required_phantom_git_commit_hash=required_phantom_git_commit_hash,
            )
            pb.checkout_phantom_version(
                phantom_dir=phantom_dir,
                required_phantom_git_commit_hash=required_phantom_git_commit_hash,
            )

    def test_checkout_phantom_version_dirty(self):

        with tempfile.TemporaryDirectory() as tmpdirname:
            phantom_dir = pathlib.Path(tmpdirname) / 'phantom_dir'
            pb.get_phantom(phantom_dir)
            required_phantom_git_commit_hash = (
                '6666c55feea1887b2fd8bb87fbe3c2878ba54ed7'
            )
            (phantom_dir / 'src/main/phantom.F90').unlink()
            pb.checkout_phantom_version(
                phantom_dir=phantom_dir,
                required_phantom_git_commit_hash=required_phantom_git_commit_hash,
            )


class TestPhantomPatch(unittest.TestCase):
    """Test patching Phantom."""

    def test_phantom_patch(self):

        with tempfile.TemporaryDirectory() as tmpdirname:
            phantom_dir = pathlib.Path(tmpdirname) / 'phantom_dir'
            pb.get_phantom(phantom_dir)
            required_phantom_git_commit_hash = (
                '6666c55feea1887b2fd8bb87fbe3c2878ba54ed7'
            )
            pb.checkout_phantom_version(
                phantom_dir=phantom_dir,
                required_phantom_git_commit_hash=required_phantom_git_commit_hash,
            )
            phantom_patch = pathlib.Path(__file__).parent / 'stub' / 'test.patch'
            pb.patch_phantom(phantom_dir=phantom_dir, phantom_patch=phantom_patch)
            kwargs = {'phantom_dir': phantom_dir, 'phantom_patch': phantom_patch}
            self.assertRaises(PatchError, pb.patch_phantom, **kwargs)


class TestBuildPhantom(unittest.TestCase):
    """Test building Phantom."""

    def test_build_phantom(self):

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
            self.assertRaises(HDF5LibraryNotFound, pb.build_phantom, **kwargs)
            kwargs = {
                'phantom_dir': phantom_dir,
                'setup': 'FakeSetup',
                'system': 'gfortran',
            }
            self.assertRaises(CompileError, pb.build_phantom, **kwargs)


if __name__ == '__main__':
    unittest.main(verbosity=2)
