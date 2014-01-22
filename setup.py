#!/usr/bin/env python
from setuptools import setup
from pip.req import parse_requirements

install_reqs = parse_requirements("REQUIREMENTS.txt")
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name = "mixpanel-cli",
    version = "0.1.0",
    author = "Atomic Labs, LLC",
    author_email = "ops@atomicmgmt.com",
    description = ("Command line tool for querying the Mixpanel API"),
    license = "MIT",
    url = "http://www.atomicmgmt.com",
    packages=["mixpanel_cli"],
    install_requires=reqs
)
