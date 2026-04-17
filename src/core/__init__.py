"""pr-review-core public package metadata."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("pr-review-core")
except PackageNotFoundError:  # pragma: no cover - only used from an uninstalled source tree
    __version__ = "0+unknown"
