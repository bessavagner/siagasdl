"""
    Package siagasdl

    <Write the package's description here>
"""

import logging
from logging import NullHandler
from logging.config import dictConfig
from importlib.metadata import version

from .settings import CONFIG_LOG

from .core import *  # The core module is the packages's API
from . import utils
from . import constants
from . import collector

dictConfig(CONFIG_LOG)
__version__ = version("siagasdl")

# Set default logging handler to avoid \"No handler found\" warnings.
logging.getLogger(__name__).addHandler(NullHandler())
