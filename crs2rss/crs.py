import json
import logging
from dataclasses import dataclass, field
from random import randint
from typing import List

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

logger = logging.getLogger()

URL = f"https://crsreports.congress.gov/search/results?term=&r={randint(10000000,99999999)}&orderBy=Date"
# A report entry looks like this:
# {
#     "Authors": [
#         {"FirstName": "<FULL NAME>", "SeqNumber": 1},
#     ],
#     "Coordinators": [
#         {"FirstName": "<FULL NAME>", "SeqNumber": 1},
#     ],
#     "CoverDate": "yyyy-mm-ddT00:00:00",
#     "ProductNumber": "xdddddd",
#     "ProductTypeCode": "x",
#     "Title": "<TITLE>",
#     "IconName": "x",
#     "NumberOfPages": "dd",
#     "HasPreviousVer": "<Y/N>",
#     "PreviousVersions": "<str>",
#     "CurrentSeqNumber": "d",
#     "PublicationDate": "yyyyddmmhhmmss.000000",
#     "StatusFlag": "Active",
# }


@dataclass
class CrsReport:
    title: str
    pub_date: str
    author: str
    report_id: str
    product_type_code: str
    icon_name: str
    number_of_pages: str
    has_previous_ver_str: str
    current_seq_number: str
    url: str = field(init=False)
    has_previous_ver: bool = field(init=False)
    ordinal_seq_number: str = field(init=False)
    id: str = field(init=False)

    def __post_init__(self):
        self.url = f"https://crsreports.congress.gov/product/pdf/{self.product_type_code}/{self.report_id}"
        self.has_previous_ver = self.has_previous_ver_str == "Y"
        n = int(self.current_seq_number)
        if 11 <= (n % 100) <= 13:
            suffix = "th"
        else:
            suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
        self.ordinal_seq_number = str(n) + suffix
        self.id = f"https://crsreports.congress.gov/product/pdf/{self.product_type_code}/{self.report_id}/{self.current_seq_number}"


def get_latest_crs_entries(selenium_driver: webdriver) -> List[CrsReport]:
    reports = []
    for url in [URL, URL + "&pageNumber=2", URL + "&pageNumber=3"]:
        selenium_driver.get(url)

        # The Selenium driver contains the entire chome surrounding the HTTP response. In this case,
        # the response from crsreports.congress.gov is a JSON document, and the chrome contains
        # a `<div id="json">` element with the response data.
        try:
            body = selenium_driver.find_element(By.ID, "json")
            response_doc = json.loads(body.text)
        except NoSuchElementException as ex:
            logger.critical("Couldn't find JSON: %s", ex)
            logger.info("Returned HTTP body: %s", selenium_driver.page_source)
            return
        except json.JSONDecodeError as ex:
            logger.warning("bad payload: %s", ex)
            return

        for entry in response_doc["SearchResults"]:
            report = CrsReport(
                entry["Title"],
                entry["CoverDate"],
                ", ".join([x["FirstName"] for x in entry["Authors"]]),
                entry["ProductNumber"],
                entry["ProductTypeCode"],
                entry["IconName"],
                entry["NumberOfPages"],
                entry["HasPreviousVer"],
                entry["CurrentSeqNumber"],
            )
            reports.append(report)

        return reports
