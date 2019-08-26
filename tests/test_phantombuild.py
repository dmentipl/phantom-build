"""
Testing phantombuild.
"""

import pathlib
import shutil
import unittest

import phantombuild as pb


class TestGetPhantom(unittest.TestCase):
    """Test getting Phantom from bitbucket."""

    def test_get_phantom(self):

        phantom_dir = pathlib.Path('phantom_dir')
        pb.get_phantom(phantom_dir)
        pb.get_phantom(phantom_dir)
        shutil.rmtree(phantom_dir)


class TestCheckPhantom(unittest.TestCase):
    """Test checking Phantom version."""

    def test_check_phantom_version(self):

        phantom_dir = pathlib.Path('phantom_dir')
        pb.get_phantom(phantom_dir)
        required_phantom_git_sha = '6666c55feea1887b2fd8bb87fbe3c2878ba54ed7'
        phantom_patch = None
        pb.check_phantom_version(phantom_dir, required_phantom_git_sha, phantom_patch)
        shutil.rmtree(phantom_dir)


class TestPhantomPatch(unittest.TestCase):
    """Test patching Phantom."""

    def test_phantom_patch(self):

        phantom_dir = pathlib.Path('phantom_dir')
        pb.get_phantom(phantom_dir)
        required_phantom_git_sha = '6666c55feea1887b2fd8bb87fbe3c2878ba54ed7'
        phantom_patch = pathlib.Path(__file__).parent / 'stub' / 'test.patch'
        pb.check_phantom_version(phantom_dir, required_phantom_git_sha, phantom_patch)
        shutil.rmtree(phantom_dir)


if __name__ == '__main__':
    unittest.main(verbosity=2)
