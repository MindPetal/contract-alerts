# coding: utf-8

from setuptools import setup, find_packages  # noqa: H301

NAME = "client"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.15", "six >= 1.10", "certifi", "python-dateutil", "playwright == 1.51.0"]

setup(
    name=NAME,
    version=VERSION,
    description="rest client",
    author_email="",
    url="",
    keywords=[],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description=""
)
