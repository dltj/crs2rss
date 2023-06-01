import datetime
import os
import sqlite3
import time
from datetime import datetime, timedelta, timezone
from textwrap import dedent
from typing import List

from mastodon import Mastodon

from crs2rss.config import settings
from crs2rss.crs import CrsReport

HISTORY_DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS crs_reports_mastodon (
    id VARCHAR PRIMARY KEY, 
    post_timestamp INTEGER,
    post_url VARCHAR,
    repost_timestamp INTEGER,
    repost_url VARCHAR)
"""

HISTORY_DB_SELECT = (
    "SELECT post_timestamp, repost_timestamp FROM crs_reports_mastodon WHERE id=?"
)

HISTORY_DB_INSERT_POST = "INSERT INTO crs_reports_mastodon VALUES (?, ?, ?, ?, ?)"

HISTORY_DB_UPDATE_REPOST = (
    "UPDATE crs_reports_mastodon SET repost_timestamp=? repost_url=? WHERE id=?"
)


def mastodon_post(reports: List[CrsReport]) -> None:
    mastodon = Mastodon(
        api_base_url="https://botsin.space/",
        access_token=settings.mastodon.api_key,
    )
    datetime_now = datetime.now(timezone.utc)

    script_dir = os.path.dirname(__file__)
    history_db_file = os.path.join(script_dir, "..", "report_history.sqlite")
    history_db = sqlite3.connect(database=history_db_file)
    history_db.execute(HISTORY_DB_SCHEMA)
    history_db.row_factory = sqlite3.Row
    cur = history_db.cursor()

    for report in reports:
        report_uri = report.id
        mastodon_post_str = dedent(
            f"""\
            Congressional Research Service Report

            {report.title}
            {report.url}
            by {report.author}. {report.number_of_pages} page(s). 
        """
        )
        if report.has_previous_ver:
            mastodon_post_str += dedent(
                f"""
                This is the { report.ordinal_seq_number } published version. See https://crsreports.congress.gov/product/details?prodcode={ report.report_id } for previous versions.
            """
            )
        cur.execute(HISTORY_DB_SELECT, (report_uri,))
        if db_record := cur.fetchone():
            # We've seen this post before; see if it is time to repost it
            post_timestamp = datetime.fromisoformat(db_record["post_timestamp"])
            repost_timestamp = db_record["repost_timestamp"]
            if not repost_timestamp and datetime_now > post_timestamp + timedelta(
                hours=12
            ):
                masto_resp = mastodon.toot(f"REPOST {mastodon_post_str}")
                cur.execute(
                    HISTORY_DB_UPDATE_REPOST,
                    (datetime_now, masto_resp["url"], report_uri),
                )
        else:
            # We haven't seen it before; post it for the first time
            masto_resp = mastodon.toot(f"NEW {mastodon_post_str}")
            cur.execute(
                HISTORY_DB_INSERT_POST,
                (report_uri, datetime_now, masto_resp["url"], "", ""),
            )
        history_db.commit()
        time.sleep(1)

    history_db.close()
