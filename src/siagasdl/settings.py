"""
    This module provides the default settings of the
    package test
"""

from importlib import metadata


package = metadata.metadata('siagasdl')

name = package['name']
version = package['version']
author = package['author']
author_email = package['author-email']
summary = package['summary']

TITLE = name
DELIMITER = len(TITLE)*"="
HEADER = f"""
{DELIMITER}
{TITLE}
Version: {version}
Description: {summary}
Authors: {author}
{DELIMITER}
"""

CONFIG_LOG = {
    "version": 1,
    "formatters": {
        "client": {
            "format": "%(levelname)s: %(message)s"
        },
        "standard": {
            "format": "%(levelname)s - function: (%(name)s at %(funcName)s line %(lineno)d): %(message)s"
        }
    },
    "handlers": {
        "client": {
            "class": "logging.StreamHandler",
            "formatter": "client",
            "level": "INFO"
        },
        "standard": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "DEBUG"
        }
    },
    "root": {
        "handlers": [
            "standard"
        ],
        "level": "DEBUG"
    },
    "loggers": {
        "client": {
            "handlers": [
                "client"
            ],
            "level": "DEBUG",
            "propagate": False
        },
        "standard": {
            "handlers": [
                "standard"
            ],
            "level": "DEBUG",
            "propagate": False
        }
    }
}
