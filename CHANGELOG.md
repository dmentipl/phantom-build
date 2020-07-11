# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Types of changes:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

## [Unreleased]

## [0.2.0] - 2020-07-11

### Added

- Add setting up Phantom runs by calling phantomsetup with a Phantom `.setup` file.
- Add a config file in TOML format to specify parameters for building Phantom and for setting up runs.
- Add jinja templating to the TOML file to set up many runs.
- Add command line program to build Phantom and set up runs.

## [0.1.4] - 2019-09-24

### Added

- Add logging using Python standard library.

## [0.1.3] - 2019-08-28

### Changed

- Use git checkout rather than git restore.

## [0.1.2] - 2019-08-28

### Fixed

- Fix ssh URL for Phantom bitbucket repository.

## [0.1.1] - 2019-08-27

### Changed

- Make HDF5 optional for Phantom builds.
- Only support Python >= 3.7.

## [0.1.0] - 2019-08-27

- Initial release.
