#! /usr/bin/env python

import requests
import os
from requests.exceptions import RequestException

BUILD_URL = 'https://readthedocs.com/api/v3/projects/canonical-ubuntu-documentation-library/versions/latest/builds/'
PROJECT_LIST_URL = 'https://readthedocs.com/api/v3/projects/'
TOKEN = os.environ.get("TOKEN")

def main():

    response = authorised_post(BUILD_URL, TOKEN)
    if response.status_code != 202:
        raise Exception("Build trigger not accepted")
    else:
        print("Build triggered")

# POST query a URL with an auth token
def authorised_post(url, token):

    HEADERS = {'Authorization': f'token {token}'}
    try:
        response = requests.post(url, headers=HEADERS, timeout=10)
    except RequestException as e:
        print(f"Failed query_api(): {url}")
        raise SystemExit(e)
    return response


if __name__ == "__main__":
    main()