"""
Phantom build
=============

phantombuild is designed to make building Phantom easier.

See [Phantom](https://github.com/danieljprice/phantom) for details on
Phantom.

Daniel Mentiplay, 2019-2020.
"""

from .phantombuild import (
    build_phantom,
    checkout_phantom_version,
    get_phantom,
    patch_phantom,
    read_config,
    schedule_job,
    setup_calculation,
    write_config,
)

__all__ = [
    'build_and_setup',
    'build_phantom',
    'checkout_phantom_version',
    'get_phantom',
    'patch_phantom',
    'read_config',
    'schedule_job',
    'setup_calculation',
    'write_config',
]

__version__ = '0.2.0'
