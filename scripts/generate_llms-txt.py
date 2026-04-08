#! /usr/bin/env python

# NOTE: This script requires an RTD API token to be provided through the environment to function
#
# Create an API token https://app.readthedocs.com/accounts/tokens/
# export TOKEN=<token>

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

EXCEPTIONS = [
    "https://documentation.ubuntu.com/security-team/"
]

# Check if debugging: export DEBUGGING=1
if os.getenv("DEBUGGING"):
    logging.basicConfig(level=logging.DEBUG)

def scan_subprojects():
    """Create list of subprojects with URLs for main version"""

    subprojects = {}
    url = SUBPROJECT_URL

    while url:
        response = authorised_get(url, TOKEN)
        data = response.json()

        for item in data["results"]:
            doc_url = item["child"]["urls"]["documentation"]
            name = item["child"]["name"]

            if doc_url in EXCEPTIONS:
                logging.debug(f"{doc_url} is listed in exceptions, skipping")
                continue

            subprojects[name] = doc_url
            logging.debug(f"Found subproject: {name} -> {doc_url}")

        url = data.get("next")

    return subprojects

def find_llms_txt(subproject_urls):
    """Check which subprojects have an LLMS.txt file and return a list of URLs if LLMS.txt files exist"""

    llms_urls = []

    for name, doc_url in subproject_urls.items():
        llms_url = f"{doc_url}llms.txt"
        logging.debug(f"Checking existence of llms.txt for {name}: {llms_url}")

        try:
            code = requests.get(llms_url, timeout=TIMEOUT, allow_redirects=False).status_code
        except RequestException:
            logging.debug(f"Request failed for {llms_url}")
            continue

        logging.debug(f"{llms_url} STATUS={code}")

        if code == 200:
            llms_urls.append((name, llms_url))
            logging.debug(f"Adding {name} llms.txt to the list")

    return llms_urls

def create_main_llms_txt(llms_urls):
    """Create a LLMS.txt file for the main project containing an inventory of all subproject LLMS.txt files"""

    sorted_urls = sorted(llms_urls, key=lambda x: x[0].lower())

    lines = [
        "# Ubuntu documentation library",
        "",
        "> The Ubuntu documentation library is an index of documentation for Ubuntu and related Canonical projects.",
        "",
        "## Documentation",
        "",
    ]

    for name, url in sorted_urls:
        lines.append(f"- [{name}]({url})")

    try:
        logging.debug("Writing llms.txt")
        with open("llms.txt", "w") as f:
            f.write("\n".join(lines) + "\n")
    except Exception as e:
        raise e


def main():
    """Generates an llms.txt pointing to the llms.txt files of subprojects of the Ubuntu Documentation Library"""

    subprojects = scan_subprojects()
    llms_urls = find_llms_txt(subprojects)
    create_main_llms_txt(llms_urls)


# GET query a URL with an auth token
def authorised_get(url, token):
    """Uses a token to auth and GET a URL"""


    logging.debug(f"Querying {url}")
    HEADERS = {"Authorization": f"token {token}"}
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        return response
    except RequestException as e:
        raise RuntimeError(f"Failed authorised_get(): {url}") from e

if __name__ == "__main__":
    main()
