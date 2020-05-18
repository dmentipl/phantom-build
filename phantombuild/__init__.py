"""
Phantom build
=============

phantombuild is designed to make building Phantom easier.

See [Phantom](https://phantomsph.bitbucket.io/) for details on Phantom.

Daniel Mentiplay, 2019-2020.
"""

from .phantombuild import (
    build_and_setup,
    build_phantom,
    checkout_phantom_version,
    get_phantom,
    patch_phantom,
    setup_calculation,
    schedule_job,
)

__all__ = [
    'build_and_setup',
    'build_phantom',
    'checkout_phantom_version',
    'get_phantom',
    'patch_phantom',
    'schedule_job',
    'setup_calculation',
]
__version__ = '0.1.4'
