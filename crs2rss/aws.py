import datetime
import logging

from crs2rss.atom import generate_rss
from crs2rss.crs import get_latest_crs_entries
from crs2rss.drivers.lambda_layer_driver import selenium_driver

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def genRss(event, context):
    current_time = datetime.datetime.now().time()
    name = context.function_name
    logger.info("Your cron function " + name + " ran at " + str(current_time))

    reports = get_latest_crs_entries(selenium_driver)
    if reports:
        feed = generate_rss(reports)
        return feed
