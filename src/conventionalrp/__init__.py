from . import _core

__all__ = ["_core", "__version__"]

from importlib.metadata import version
from pkg_resources import get_distribution

try:
    # For Python 3.8+
    __version__ = version("conventionalrp")
except ImportError:
    try:
        # For Python < 3.8
        __version__ = get_distribution("conventionalrp").version
    except Exception:
        raise ImportError("Failed to get version")
