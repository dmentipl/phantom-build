Phantom build
=============

> phantom-build is designed to make building Phantom easier.

The main aim is to have reproducible Phantom builds for writing reproducible papers.

Install
-------

Install phantom-build with pip

```
pip install phantombuild
```

Usage
-----

Import phantom-build

```python
>>> import phantombuild as pb
```

phantom-build has four main functions:

- `get_phantom` is used to clone Phantom from bitbucket, or to check if it is already cloned.
- `check_phantom_version` is used to check out a particular Phantom version based on a git commit hash.
- `patch_phantom` is used to apply patches.
- `build_phantom` is for compiling Phantom with particular Makefile options.

Examples
--------

Here we check out a particular version of Phantom based on the git commit hash.

```python
# Clone Phantom
phantom_dir = pathlib.Path('~/repos/phantom').expanduser()
pb.get_phantom(phantom_dir)

# Checkout particular commit
required_phantom_git_commit_hash = '6666c55feea1887b2fd8bb87fbe3c2878ba54ed7'
pb.check_phantom_version(phantom_dir, required_phantom_git_commit_hash)
```

Then we apply a patch.

```python
# Apply patch
phantom_patch = CODE_DIR / 'dustybox.patch'
pb.patch_phantom(phantom_dir, phantom_patch)
```

Now we build Phantom with particular Makefile options.

```python
# Makefile options
setup = 'dustybox'
system = 'gfortran'
extra_makefile_options = {'MAXP': '10000000'}
hdf5_location = pathlib.Path('/usr/local/opt/hdf5')

# Compile Phantom
pb.build_phantom(
    phantom_dir,
    setup,
    system,
    hdf5_location,
    extra_makefile_options
)
```
