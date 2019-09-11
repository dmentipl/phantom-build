import io
import pathlib
import re

from setuptools import setup

version = re.search(
    r'__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
    io.open('phantombuild/__init__.py', encoding='utf_8_sig').read(),
).group(1)

long_description = (pathlib.Path(__file__).parent / 'README.md').read_text()

setup(
    name='phantombuild',
    version=version,
    author='Daniel Mentiplay',
    packages=['phantombuild'],
    url='http://github.com/dmentipl/phantom-build',
    license='MIT',
    description='Phantom build',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.7',
)
