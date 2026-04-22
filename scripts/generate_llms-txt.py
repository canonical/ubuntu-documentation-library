#! /usr/bin/env python

# NOTE: This script requires an RTD API token to be provided through the environment to function
#
# Create an API token https://app.readthedocs.com/accounts/tokens/
# export TOKEN=<token>

import requests
import os
import datetime
import logging
import yaml
from requests.exceptions import RequestException

PROJECT_URL = (
    "https://readthedocs.com/api/v3/projects/canonical-ubuntu-documentation-library/"
)
SUBPROJECT_URL = "https://readthedocs.com/api/v3/projects/canonical-ubuntu-documentation-library/subprojects/?limit=75"
TOKEN = os.environ["TOKEN"]
TIMEOUT = 10  # seconds
EXTRA_ENTRIES_FILE = os.path.join(os.path.dirname(__file__), "../custom_llms_entries.yml")

EXCEPTIONS = [
    "https://documentation.ubuntu.com/security-team/"
]

# Check if debugging: export DEBUGGING=1
if os.getenv("DEBUGGING"):
    logging.basicConfig(level=logging.DEBUG)

def scan_subprojects() -> dict:
    """Create list of subprojects with URLs for main version"""

    subprojects = {}
    url = SUBPROJECT_URL

    while url:
        response = authorised_get(url, TOKEN)
        data = response.json()

        for item in data["results"]:
            doc_url = item["child"]["urls"]["documentation"]
            name = item["child"]["name"]
            version = item["child"]["default_version"]

            if doc_url in EXCEPTIONS:
                logging.debug(f"{doc_url} is listed in exceptions, skipping")
                continue

            subprojects[name] = {version: doc_url}
            logging.debug(f"Found subproject: {name} -> {doc_url}")

        url = data.get("next")

    return subprojects

def find_llms_txt(subproject_urls: dict) -> dict:
    """Check which subprojects have an LLMS.txt file and return a list of URLs if LLMS.txt files exist"""

    llms_urls = {}

    for name in subproject_urls.keys():
        for version, doc_url in subproject_urls[name].items():
            llms_url = f"{doc_url}llms.txt"
            logging.debug(f"Checking existence of llms.txt for {name} ({version}): {llms_url}")

        try:
            code = requests.get(llms_url, timeout=TIMEOUT, allow_redirects=False).status_code
        except RequestException:
            logging.debug(f"Request failed for {llms_url}")
            continue

        logging.debug(f"{llms_url} STATUS={code}")

        if code == 200:
            llms_urls[name] = {version: {"url": llms_url, "description": ""}}
            logging.debug(f"Adding {name} ({version}) llms.txt to the list")

    return llms_urls

def add_descriptions(llms_urls: dict) -> dict:
    """Checks the LLMS.txt files for descriptions and adds them to the dictionary"""

    for product in llms_urls.keys():
        for version in llms_urls[product].keys():
            try:
                response = requests.get(llms_urls[product][version]["url"], timeout=TIMEOUT)
                response.raise_for_status()
                lines = response.text.splitlines()
                description = lines[2] if len(lines) > 2 else ""
                llms_urls[product][version] = {"url": llms_urls[product][version]["url"], "description": description[2:] if description.startswith("> ") else description}
            except RequestException:
                logging.debug(f"Failed to get description for {product} ({version}) at {llms_urls[product][version]['url']}")
                llms_urls[product][version] = {"url": llms_urls[product][version]["url"], "description": ""}

    return llms_urls

def add_custom_entries(file: str, llms_urls: dict) -> dict:
    """Takes a YAML file and adds custom entries to the llms.txt file"""

    logging.debug(f"Loading extra entries from {file}")

    with open(file, "r") as f:
        data = yaml.safe_load(f)

    if data == None:
        logging.debug(f"No data found in {file}")
        return llms_urls

    logging.debug(f"Loading {data}")

    for item in data["projects"]:
        logging.debug(f"assessing {item}")
        product = item["name"]
        versions = item["versions"].keys()
        if product not in llms_urls:
            llms_urls[product] = {}
        for version in versions:
            llms_url = item["versions"][version]["url"]
            description = ""
            if "description" in item["versions"][version]:
                description = item["versions"][version]["description"]
            try:
                code = requests.get(llms_url, timeout=TIMEOUT, allow_redirects=False).status_code
            except RequestException:
                logging.debug(f"Request failed for {llms_url}")
                continue
            if code == 200:
                llms_urls[product][version] = {"url": llms_url, "description": description}

    return llms_urls

def create_main_llms_txt(llms_urls: dict) -> None:
    """Create a LLMS.txt file for the main project containing an inventory of all subproject LLMS.txt files"""

    logging.debug(f"creating file from: {llms_urls}")

    lines = [
        "# Ubuntu documentation library",
        "",
        "> The Ubuntu documentation library is an index of documentation for Ubuntu and related Canonical projects.",
    ]

    for item in llms_urls.keys():
        logging.debug(f"Processing item: {item}")
        lines.append(f"")
        lines.append(f"## {item}")
        if "latest" in llms_urls[item]:
            logging.debug(f"Adding latest version for {item}")
            lines.append(f"- [{item} latest documentation]({llms_urls[item]['latest']['url']}): {llms_urls[item]['latest']['description']}")
        for version in llms_urls[item].keys():
            if version == "latest":
                continue
            logging.debug(f"Processing version: {version}")
            url = llms_urls[item][version]["url"]
            description = llms_urls[item][version]["description"]
            if description == "":
                lines.append(f"- [{item} {version} documentation]({url})")
            else:
                lines.append(f"- [{item} {version} documentation]({url}): {description}")

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
    llms_urls = add_descriptions(llms_urls)
    llms_urls = add_custom_entries(EXTRA_ENTRIES_FILE, llms_urls)
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