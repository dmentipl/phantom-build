"""Phantom-build command line program."""

import click

from . import __version__
from .phantombuild import build_phantom, read_config, setup_calculation, write_config


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
    write_config(filename)


@cli.command()
@click.argument('config', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def build(ctx, config):
    """Build Phantom."""
    if len(config) == 0:
        click.echo(ctx.get_help())
        ctx.exit()
    for _config in config:
        conf = read_config(_config)
        build_phantom(**conf['phantom'])


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
        conf = read_config(_config)
        build_phantom(**conf['phantom'])
        phantom_path = conf['phantom']['path']
        for run in conf.get('runs', []):
            run_path = run.pop('path')
            setup_calculation(run_path=run_path, phantom_path=phantom_path, **run)


if __name__ == '__main__':
    cli(prog_name='python -m phantombuild')
