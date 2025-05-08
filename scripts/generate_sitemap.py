#! /usr/bin/env python

# NOTE: This script requires an RTD API token to be provided through the environment to function

import requests
import os
import datetime
import logging
from requests.exceptions import RequestException

PROJECT_URL = (
    "https://readthedocs.com/api/v3/projects/canonical-ubuntu-documentation-library/"
)
SUBPROJECT_URL = "https://readthedocs.com/api/v3/projects/canonical-ubuntu-documentation-library/subprojects/?limit=50"
TOKEN = os.environ["TOKEN"]
TIMEOUT = 10  # seconds
EXCEPTIONS_LIST = ["https://documentation.ubuntu.com/security-team/en/latest/"]

# Check if debugging
if os.getenv("DEBUGGING"):
    logging.basicConfig(level=logging.DEBUG)


def main():

    # print(authorised_get("https://documentation.ubuntu.com/dedicated-snap-store/", TOKEN).status_code)
    # return

    template_sitemap = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'

    # Get and update subproject data
    subprojects = authorised_get(SUBPROJECT_URL, TOKEN)
    subproject_data = subprojects.json()
    children = {}

    for item in subproject_data["results"]:

        if item["child"]["urls"]["documentation"] in EXCEPTIONS_LIST:
            continue

        logging.debug(
            f"Checking existence of sitemap for {item["child"]["urls"]["documentation"]}"
        )
        code = requests.get(
            f"{item["child"]["urls"]["documentation"]}sitemap.xml"
        ).status_code
        logging.debug(
            f"{item["child"]["urls"]["documentation"]}sitemap.xml STATUS={str(code)}"
        )
        if code == 200:

            modified = datetime.datetime.fromisoformat(
                item["child"]["modified"]
            ).strftime("%Y-%m-%d")
            children.update(
                {f"{item["child"]["urls"]["documentation"]}sitemap.xml": modified}
            )
            logging.debug(
                f"Adding {item["child"]["urls"]["documentation"]} to the sitemap"
            )

    for key, value in children.items():
        template_sitemap = "{}\n{}".format(
            template_sitemap, template_sitemap_section(key, value)
        )

    # Write sitemap
    try:
        logging.debug("writing sitemap")
        sitemap = open("sitemap.xml", "w")
        sitemap.write(f"{template_sitemap}\n</urlset>")
    except Exception as e:
        raise e


# Format URL and modification date into sitemap compliant string
def template_sitemap_section(loc, lastmod):
    template = f"<url>\n<loc>{loc}</loc>\n<lastmod>{lastmod}</lastmod>\n</url>"
    return template


# GET query a URL with an auth token
def authorised_get(url, token):

    logging.debug(f"Querying {url}")
    HEADERS = {"Authorization": f"token {token}"}
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        return response
    except RequestException as e:
        raise RuntimeError(f"Failed authorised_get(): {url}") from e


if __name__ == "__main__":
    main()
