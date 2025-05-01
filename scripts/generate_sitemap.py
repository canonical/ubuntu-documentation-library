#! /usr/bin/env python

import requests
import os
import datetime

PROJECT_URL = 'https://readthedocs.com/api/v3/projects/canonical-ubuntu-documentation-library/'
SUBPROJECT_URL = 'https://readthedocs.com/api/v3/projects/canonical-ubuntu-documentation-library/subprojects/?limit=50'
TOKEN = os.environ["TOKEN"]

def main():

    template_sitemap = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'

    # Get and update main project data
    project = authorised_get(PROJECT_URL, TOKEN)
    project_data = project.json()
    template_sitemap = "{}\n{}".format(template_sitemap, template_sitemap_section("https://documentation.ubuntu.com/en/latest/", datetime.datetime.fromisoformat(project_data["modified"]).strftime("%Y-%m-%d")))

    # Get and update subproject data
    subprojects = authorised_get(SUBPROJECT_URL, TOKEN)
    subproject_data = subprojects.json()
    children = {}

    for item in subproject_data["results"]:
        modified = datetime.datetime.fromisoformat(item["child"]["modified"]).strftime("%Y-%m-%d")
        children.update({item["child"]["urls"]["documentation"]: modified})

    for key, value in children.items():
        template_sitemap = "{}\n{}".format(template_sitemap, template_sitemap_section(key, value))

    # Write sitemap
    sitemap = open("sitemap.xml", "w")
    sitemap.write(template_sitemap + "\n</urlset>")

# Format URL and modification date into sitemap compliant string
def template_sitemap_section(loc, lastmod):
    template = "<url>\n<loc>{}</loc>\n<lastmod>{}</lastmod>\n</url>".format(loc, lastmod)
    return template

# GET query a URL with an auth token
def authorised_get(url, token):

    HEADERS = {'Authorization': f'token {token}'}
    response = requests.get(url, headers=HEADERS)

    return response

if __name__ == "__main__":
    main()