"""Phantom-build setup.py."""

import io
import pathlib
import re

from setuptools import setup

version = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    io.open('phantombuild/__init__.py', encoding='utf_8_sig').read(),
).group(1)

long_description = (pathlib.Path(__file__).parent / 'README.md').read_text()

install_requires = ['click', 'jinja2', 'tomlkit']

setup(
    name='phantombuild',
    version=version,
    author='Daniel Mentiplay',
    packages=['phantombuild'],
    url='http://github.com/dmentipl/phantom-build',
    license='MIT',
    description='phantom-build is designed to make building Phantom easier',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=install_requires,
    include_package_data=True,
    python_requires='>=3.7',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
)
