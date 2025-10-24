"""
Conventional Role Play SDK (ConventionalRP)
"""

import sys
from importlib.metadata import version

from . import _core
from .core import Parser, Processor, Rule, RuleEngine
from .utils import (
    setup_logging,
    get_logger,
    ConventionalRPError,
    ParserError,
    RuleError,
    ProcessorError,
    ValidationError,
    ConfigurationError,
)

__all__ = [
    "Parser",
    "Processor",
    "Rule",
    "RuleEngine",
    "setup_logging",
    "get_logger",
    "ConventionalRPError",
    "ParserError",
    "RuleError",
    "ProcessorError",
    "ValidationError",
    "ConfigurationError",
    "__version__",
]

if sys.version_info >= (3, 8):
    __version__ = version("conventionalrp")
elif sys.version_info < (3, 8):
    from pkg_resources import get_distribution

    __version__ = get_distribution("conventionalrp").version

_default_logger = setup_logging(level="INFO")

