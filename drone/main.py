import click
import config

@click.command()
@click.option('--resolution', default=config.resolution, help='Resolution of your ')
def main():
    pass
