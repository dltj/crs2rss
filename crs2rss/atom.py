import datetime
from typing import List

from jinja2 import Environment, PackageLoader, select_autoescape

from crs2rss.crs import CrsReport


def generate_rss(reports: List[CrsReport]) -> str:
    env = Environment(loader=PackageLoader("crs2rss"), autoescape=select_autoescape())
    template = env.get_template("atom.j2.xml")
    template_variables = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(
            sep="T", timespec="seconds"
        ),
        "reports": reports,
    }
    feed = template.render(template_variables)

    return feed
