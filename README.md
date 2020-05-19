Phantom build
=============

> phantom-build: make building Phantom easier.

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

Requirements
------------

Python 3.7+. [Click](https://click.palletsprojects.com/), [tomlkit](https://github.com/sdispater/tomlkit).

Usage
-----

Import phantom-build

```python
>>> import phantombuild
```

phantom-build has some useful functions:

- Use `get_phantom` to clone Phantom from the [bitbucket repository](https://bitbucket.org/danielprice/phantom), or to check if already cloned.
- Use `checkout_phantom_version` to check out a particular Phantom version based on a git commit hash.
- Use `patch_phantom` to apply patches.
- Use `build_phantom` to compile Phantom with particular Makefile options.
- Use `setup_calculation` to set up a calculation with phantomsetup.
- Use `schedule_job` to schedule a calculation with a job scheduler, e.g. Slurm.

Examples
--------

### A reproducible Phantom paper

Say you want to have a reproducible Phantom build for a paper. You want to work from a particular version of Phantom, and you need to apply patches to that version.

1. First, clone Phantom.

    ```python
    # Clone Phantom
    phantom_path = '~/phantom'
    phantombuild.get_phantom(path=phantom_path)
    ```

2. Now, check out a particular version of Phantom based on the git commit hash.

    ```python
    # Checkout particular commit
    version = '6666c55f'
    phantombuild.checkout_phantom_version(path=phantom_path, version=version)
    )
    ```

3. Then, apply your patch.

    ```python
    # Apply patch
    patch = 'phantom-6666c55f.patch'
    phantombuild.patch_phantom(path=phantom_path, patch=patch)
    ```

4. Now, build Phantom with particular Makefile options.

    ```python
    # Makefile options
    setup = 'disc'
    system = 'gfortran'
    extra_makefile_options = {'MAXP': '10000000'}
    hdf5_path = '/usr/local/opt/hdf5'

    # Compile Phantom
    phantombuild.build_phantom(
        path=phantom_path,
        setup=setup,
        system=system,
        hdf5_path=hdf5_path,
        extra_options=extra_options,
    )
    ```

5. Set up your calculation with `phantomsetup`.

    ```python
    # Options for particular calculation
    prefix = 'disc'
    setup_file = '~/repos/paper/disc_a.setup'
    in_file = '~/repos/paper/disc_a.in'
    run_path = '~/runs/disc_a'

    # Set up calculation
    phantombuild.setup_calculation(
        prefix=prefix,
        setup_file=setup_file,
        in_file=in_file,
        run_path=run_path,
        phantom_path=phantom_path,
    )
    ```

6. Schedule your job with Slurm.

    ```python
    job_file = '~/repos/paper/slurm.sh'
    phantombuild.schedule_job(run_path=run_path, job_file=job_file)
    ```

You can write the above into a script included with the git repository of the paper to help make your paper reproducible. Of course, you also need to include all the Phantom `.in` and `.setup` files. For managing those files, see [phantom-config](https://github.com/dmentipl/phantom-config). For setting up Phantom simulations in pure Python (no Fortran required), see (the work in progress) [phantom-setup](https://github.com/dmentipl/phantom-setup).
