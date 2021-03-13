Phantom build
=============

> phantom-build: make building Phantom easier.

The main use case for phantom-build is to make it easy to generate reproducible [Phantom](https://github.com/danieljprice/phantom) builds for writing reproducible papers.

[![Build Status](https://github.com/dmentipl/phantom-build/actions/workflows/tests.yml/badge.svg)](https://github.com/dmentipl/phantom-build/actions)
[![Coverage Status](https://coveralls.io/repos/github/dmentipl/phantom-build/badge.svg?branch=master)](https://coveralls.io/github/dmentipl/phantom-build?branch=master)
[![PyPI](https://img.shields.io/pypi/v/phantombuild)](https://pypi.org/project/phantombuild/)

Table of contents
-----------------

* [Install](#install)
* [Requirements](#requirements)
* [Usage](#usage)
    * [From the command line](#from-the-command-line)
    * [Using Python](#using-python)
* [Details](#details)
    * [A reproducible Phantom paper](#a-reproducible-phantom-paper)
* [See also](#see-also)
    * [phantom-config](#phantom-config)
    * [phantom-setup](#phantom-setup)

Install
-------

Install phantom-build with pip

```bash
python -m pip install phantombuild
```

Requirements
------------

Python 3.7+ with [tomlkit](https://github.com/sdispater/tomlkit), [jinja](https://jinja.palletsprojects.com/), and [click](https://click.palletsprojects.com/).

Usage
-----

### From the command line

You can use phantom-build at the command line.

```bash
python -m phantombuild setup config.toml
```

The command line program reads from a TOML config file, and uses the values
within to build Phantom and set up (possibly multiple) calculations. This is an
example config file with comments explaining the structure.

```toml
# This is a phantombuild config file
# It is a TOML file, see https://github.com/toml-lang/toml

# [phantom]
#
# The first section contains information required to build Phantom. You must
# provide:
#
# - path: the path to where the Phantom repository will live
# - setup: the Phantom SETUP Makefile variable
# - system: the Phantom SYSTEM Makefile variable
#
# You can optionally provide:
#
# - version: the Phantom version to use via a git commit hash
# - patches: a list of paths to patch files if you wish to modify Phantom
# - extra_options: a list of extra Phantom Makefile options
# - hdf5_path: the path to the HDF5 installation; this directory should have
#   include and lib as sub-directories

[phantom]
path = "~/repos/phantom"
setup = "disc"
system = "ifort"
version = "d9a5507f"
patches = [
    "phantom-d9a5507f-1.patch",
    "phantom-d9a5507f-2.patch",
]
extra_options = ["MAXP=10000000", "ISOTHERMAL=no"]
hdf5_path = "/usr/local/opt/hdf5"

# [[runs]]
#
# The follow sections contain information for each run you wish to set up. You
# must provide:
#
# - prefix: the Phantom run prefix, e.g. files will be named prefix_00000.h5...
# - path: the path to the run directory
# - setup_file: the path to the phantomsetup .setup file
# - in_file: the path to the phantom .in file
#
# You can optionally provide:
#
# - job_script: the path to a Slurm job script if you wish to submit the run to
#   a Slurm job scheduler

[[runs]]
prefix = "disc"
path = "~/runs/discs/disc_a"
setup_file = "~/repos/discs/disc_a.setup"
in_file = "~/repos/discs/disc_a.in"
job_script = "~/repos/discs/slurm.sh"

[[runs]]
prefix = "disc"
path = "~/runs/discs/disc_b"
setup_file = "~/repos/discs/disc_b.setup"
in_file = "~/repos/discs/disc_b.in"
job_script = "~/repos/discs/slurm.sh"

```

### Using Python

You can use phantom-build with a Python script or from the Python REPL.

Import phantom-build.

```python
import phantombuild
```

Choose Phantom build options. Only `path`, `setup`, and `system` are required arguments; the rest are optional.

```python
# Options for Phantom build
phantom_path = '~/phantom'
version = '6666c55f'
patches = ['phantom-6666c55f.patch']
setup = 'disc'
system = 'gfortran'
extra_makefile_options = {'MAXP': '10000000', 'ISOTHERMAL': 'no'}
hdf5_path = '/usr/local/opt/hdf5'
```

Build Phantom.

```python
# Build Phantom
phantombuild.build_phantom(
    path=phantom_path,
    version=version,
    patches=patches,
    setup=setup,
    system=system,
    hdf5_path=hdf5_path,
    extra_options=extra_options,
)
```

Set options for Phantom calculation.

```python
# Options for calculation
prefix = 'disc'
setup_file = '~/repos/paper/disc_a.setup'
in_file = '~/repos/paper/disc_a.in'
run_path = '~/runs/disc_a'
job_script = '~/repos/paper/slurm.sh'
```

Set up calculation, and (optionally) schedule job with Slurm.

```python
# Set up calculation
phantombuild.setup_calculation(
    prefix=prefix,
    setup_file=setup_file,
    in_file=in_file,
    run_path=run_path,
    phantom_path=phantom_path,
    job_script=job_script,
)
```

Details
-------

The phantom-build functions `build_phantom` and `setup_calculation` rely on the following functions:

- Use `get_phantom` to clone Phantom from the [GitHub repository](https://github.com/danieljprice/phantom), or to check if already cloned.
- Use `checkout_phantom_version` to check out a particular Phantom version based on a git commit hash.
- Use `patch_phantom` to apply patches.
- Use `schedule_job` to schedule a calculation with a job scheduler, e.g. Slurm.

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

You can write the above into a script included with the git repository of the paper to help make your paper reproducible. Of course, you also need to include all the Phantom `.in` and `.setup` files. For managing those files, see [phantom-config](https://github.com/dmentipl/phantom-config).

See also
--------

### phantom-config

[phantom-config](https://github.com/dmentipl/phantom-config) is a Python package designed to parse, convert, modify, and generate Phantom config files. It also facilitates generating multiple files from dictionaries for parameter sweeps.

### phantom-setup

[phantom-setup](https://github.com/dmentipl/phantom-setup) is a (work in progress) Python package designed to set up Phantom initial conditions in pure Python, i.e. with no Fortran dependencies. It uses NumPy and Numba to achieve Fortran like performance for computationally expensive operations.
