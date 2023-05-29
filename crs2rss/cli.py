import click

from crs2rss.atom import generate_rss
from crs2rss.crs import get_latest_crs_entries
from crs2rss.drivers.local_driver import selenium_driver


@click.command()
def cli():
    reports = get_latest_crs_entries(selenium_driver)
    feed = generate_rss(reports)
    print(feed)


# pylint: disable=no-value-for-parameter
if __name__ == "__main__":
    cli()
