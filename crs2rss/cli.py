import click

from crs2rss.atom import generate_rss
from crs2rss.crs import get_latest_crs_entries


@click.command()
def cli():
    reports = get_latest_crs_entries()
    feed = generate_rss(reports)
    print(feed)


# pylint: disable=no-value-for-parameter
if __name__ == "__main__":
    cli()
