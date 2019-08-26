"""
Phantom build
-------------

phantombuild is designed to make building Phantom easier.

See [Phantom](https://phantomsph.bitbucket.io/) for details on Phantom.

Daniel Mentiplay, 2019.
"""

from .phantombuild import get_phantom, check_phantom_version, build_phantom

__all__ = ['get_phantom', 'check_phantom_version', 'build_phantom']
__version__ = '0.1.0'
