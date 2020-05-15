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

Python 3.7+.

Usage
-----

Import phantom-build

```python
>>> import phantombuild
```

phantom-build has five main functions:

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
    phantom_dir = '~/repos/phantom'
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
    phantom_patch = 'my-phantom.patch'
    phantombuild.patch_phantom(
        phantom_dir=phantom_dir, phantom_patch=phantom_patch,
    )
    ```

4. Now, build Phantom with particular Makefile options.

    ```python
    # Makefile options
    setup = 'dustydisc'
    system = 'gfortran'
    extra_makefile_options = {'MAXP': '10000000'}
    hdf5_location = '/usr/local/opt/hdf5'

    # Compile Phantom
    phantombuild.build_phantom(
        phantom_dir=phantom_dir,
        setup=setup,
        system=system,
        hdf5_location=hdf5_location,
        extra_makefile_options=extra_makefile_options,
    )
    ```

5. Set up your calculation with `phantomsetup`.

    ```python
    # Options for particular calculation
    prefix = 'mydisc'
    run_dir = '~/runs/mydisc_001'
    input_dir = '~/repos/my-paper/initial-conditions/mydisc_001'

    # Set up calculation
    phantombuild.setup_calculation(
        prefix=prefix, run_dir=run_dir, input_dir=input_dir, phantom_dir=phantom_dir
    )
    ```

6. Schedule your job with Slurm.

    ```python
    job_file = '~/repos/my-paper/slurm_script'
    phantombuild.schedule_job(run_dir=run_dir, job_file=job_file)
    ```

The variable `input_dir` is a directory that contains the Phantom `.in` and
`.setup` files with `prefix` the name of the Phantom calculation.

You can write the above into a script included with the git repository of the paper to help make your paper reproducible. Of course, you also need to include all the Phantom `.in` and `.setup` files. For managing those files, see [phantom-config](https://github.com/dmentipl/phantom-config). For setting up Phantom simulations in pure Python (no Fortran required), see [phantom-setup](https://github.com/dmentipl/phantom-setup).
