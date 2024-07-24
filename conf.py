import datetime
import sys

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Ubuntu documentation library'
author = 'Canonical Group Ltd'
copyright = "%s, %s" % (datetime.date.today().year, author)
html_favicon = '.sphinx/_static/favicon.png'

extensions = [
    'sphinx_reredirects'
    ]

exclude_patterns = ['_build', '.sphinx']

# Set up redirects (https://documatt.gitlab.io/sphinx-reredirects/usage.html)
# For example: "explanation/old-name.html": "../how-to/prettify.html",
redirects = {
    "index": "https://docs.ubuntu.com"
}
