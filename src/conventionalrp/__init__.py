import sys
from importlib.metadata import version

from . import _core

__all__ = ["_core", "__version__"]

if sys.version_info >= (3, 8):
    # For Python 3.8+
    __version__ = version("conventionalrp")
elif sys.version_info < (3, 8):
    from pkg_resources import get_distribution

    # For Python < 3.8
    __version__ = get_distribution("conventionalrp").version
