mixpanel-cli
============

This is a command line tool for querying the Mixpanel API.

Installation
------------

Requires Python3 with pip installed.

Run python setup.py install.

Usage
-----

You need to set the environment variables MIXPANEL_API_KEY and
MIXPANEL_API_SECRET to your API key and secret.

    export MIXPANEL_API_KEY="your_api_key"
    export MIXPANEL_API_KEY="your_api_secret"

Then run the tool using:

    python -m mixpanel_cli --help