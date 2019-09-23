Phantom build
=============

> phantom-build is designed to make building Phantom easier.

The main aim is to have reproducible [Phantom](https://phantomsph.bitbucket.io/) builds for writing reproducible papers.

[![Build Status](https://travis-ci.org/dmentipl/phantom-build.svg?branch=master)](https://travis-ci.org/dmentipl/phantom-build)
[![Coverage Status](https://coveralls.io/repos/github/dmentipl/phantom-build/badge.svg?branch=master)](https://coveralls.io/github/dmentipl/phantom-build?branch=master)
[![PyPI](https://img.shields.io/pypi/v/phantombuild)](https://pypi.org/project/phantombuild/)

Install
-------

Install phantom-build with pip

```bash
pip install phantombuild
```

Usage
-----

Import phantom-build

```python
>>> import phantombuild
```

phantom-build has four main functions:

- `get_phantom` is used to clone Phantom from the [bitbucket repository](https://bitbucket.org/danielprice/phantom), or to check if it is already cloned.
- `checkout_phantom_version` is used to check out a particular Phantom version based on a git commit hash.
- `patch_phantom` is used to apply patches.
- `build_phantom` is for compiling Phantom with particular Makefile options.

Examples
--------

### A reproducible Phantom paper

Say you want to have a reproducible Phantom build for a paper. You want to work from a particular version of Phantom, and you need to apply patches to that version.

1. First, clone Phantom.

    ```python
    # Clone Phantom
    phantom_dir = pathlib.Path('~/repos/phantom').expanduser()
    phantombuild.get_phantom(phantom_dir=phantom_dir)
    ```

2. Now, check out a particular version of Phantom based on the git commit hash.

    ```python
    # Checkout particular commit
    required_phantom_git_commit_hash = '6666c55feea1887b2fd8bb87fbe3c2878ba54ed7'
    phantombuild.checkout_phantom_version(
        phantom_dir=phantom_dir,
        required_phantom_git_commit_hash=required_phantom_git_commit_hash,
    )
    ```

3. Then, apply your patch.

    ```python
    # Apply patch
    phantom_patch = pathlib.Path('my-phantom.patch')
    phantombuild.patch_phantom(
        phantom_dir=phantom_dir,
        phantom_patch=phantom_patch,
    )
    ```

4. Now, build Phantom with particular Makefile options.

    ```python
    # Makefile options
    setup = 'dustybox'
    system = 'gfortran'
    extra_makefile_options = {'MAXP': '10000000'}
    hdf5_location = pathlib.Path('/usr/local/opt/hdf5')

    # Compile Phantom
    phantombuild.build_phantom(
        phantom_dir=phantom_dir,
        setup=setup,
        system=system,
        hdf5_location=hdf5_location,
        extra_makefile_options=extra_makefile_options,
    )
    ```

You can write the above into a script included with the git repository of the paper to help make your paper reproducible. Of course, you also need to include all the Phantom `.in` and `.setup` files. For managing those files, see [phantom-config](https://github.com/dmentipl/phantom-config). For setting up Phantom simulations, see [phantom-setup](https://github.com/dmentipl/phantom-setup).
