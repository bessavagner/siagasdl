"""
    Package "siagasdl"

    This module provides helpful objects
"""
import logging

from selenium.webdriver.common.keys import Keys

from .constants import DISPLAY_VALUES

logger = logging.getLogger('standard')


class Key(Keys):  # pylint: disable=too-few-public-methods
    """ "keys to use in send functions"""

    enter = Keys.RETURN
    esc = Keys.ESCAPE
    delete = Keys.DELETE
    down = Keys.ARROW_DOWN
    up = Keys.ARROW_UP
    tab = Keys.TAB
    backspace = Keys.BACK_SPACE
    control = Keys.CONTROL

def make_selector(value, by):
    return {
        "value": value,
        "by": by
    }

def document_query_selector(selector: str):
    """String to parse javascript code."""
    return f"return document.querySelector('{selector}');"


def document_query_selector_all(selector: str):
    """String to parse javascript code."""
    return f"return document.querySelectorAll('{selector}');"


def document_query_selector_click(selector: str):
    """String to parse javascript code."""
    return (
        f"const element = document.querySelector('{selector}');"
        "element.click();"
        "return element;"
    )

def is_display(value: str):
    if value not in DISPLAY_VALUES:
        logger.warning((
            'Invalid display value "%s". Valid are %s.'
            'Returning False'
        ), value, DISPLAY_VALUES)
        return "return false;"
    return f"return arguments[0].style.display == '{value}';"
