# Skeleton of a CLI

import click

import dyn53


@click.command('dyn53')
@click.argument('count', type=int, metavar='N')
def cli(count):
    """Echo a value `N` number of times"""
    for i in range(count):
        click.echo(dyn53.has_legs)
