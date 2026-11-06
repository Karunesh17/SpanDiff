"""SpanDiff: evidence-based API request comparisons."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("spandiff")
except PackageNotFoundError:
    __version__ = "0.1.0.dev0"
