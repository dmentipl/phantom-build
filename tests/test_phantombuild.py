"""
Testing phantombuild.
"""

import pathlib
import unittest

import phantombuild as pb


class TestGetPhantom(unittest.TestCase):
    """Test getting Phantom from bitbucket."""

    def test_get_phantom(self):

        phantom_dir = pathlib.Path('phantom_dir')
        pb.get_phantom(phantom_dir)


if __name__ == '__main__':
    unittest.main(verbosity=2)
