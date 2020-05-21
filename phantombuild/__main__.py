"""Phantom-build command line program."""

import click

from . import phantombuild
from . import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """Build and set up Phantom runs.

    phantombuild compiles Phantom and sets up one or more runs.
    """


@cli.command()
@click.argument('filename')
def template(filename):
    """Write a template config file to FILENAME."""
    phantombuild.write_config(filename)


@cli.command()
@click.argument('config', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def setup(ctx, config):
    """Build and set up Phantom runs.

    phantombuild compiles Phantom and sets up one or more runs. Pass in
    one CONFIG file per Phantom build config. Each CONFIG file may
    contain multiple runs.
    """
    if len(config) == 0:
        click.echo(ctx.get_help())
        ctx.exit()
    for _config in config:
        runs = phantombuild.read_config(_config)
        for run in runs:
            phantombuild.build_and_setup(**run)


if __name__ == '__main__':
    cli(prog_name='python -m phantombuild')
