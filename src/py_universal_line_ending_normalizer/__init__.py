"""Universal line ending normalizer.

This package provides a small, dependency-free API for detecting and
converting between the four line ending conventions that appear in real
text: CR (``\\r``), LF (``\\n``), CRLF (``\\r\\n``), and the Unicode
line separator (U+2028).
"""

from .core import (
    LineEnding,
    detect_line_ending,
    normalize,
    split_lines,
    iter_lines,
)

__all__ = [
    "LineEnding",
    "detect_line_ending",
    "normalize",
    "split_lines",
    "iter_lines",
]
