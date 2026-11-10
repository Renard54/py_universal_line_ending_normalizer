"""Detection and normalization of line endings.

The implementation deliberately treats a bare carriage return as a line
ending.  This is the behaviour of classic Mac OS and of many embedded
devices, and it is the only way to round-trip a file that contains no
line feed at all.  The alternative -- treating CR as ordinary whitespace
unless followed by LF -- would silently corrupt such files.
"""

from __future__ import annotations

from enum import Enum
from typing import Iterator, Tuple


class LineEnding(Enum):
    """The line ending conventions this library understands."""

    CR = "\r"
    LF = "\n"
    CRLF = "\r\n"
    LS = "\u2028"  # Unicode LINE SEPARATOR


# Order matters: CRLF must be tested before CR so that the two-character
# sequence is not mistaken for a bare carriage return.
_ORDERED_ENDINGS = (LineEnding.CRLF, LineEnding.CR, LineEnding.LF, LineEnding.LS)


def _iter_raw_segments(text: str) -> Iterator[Tuple[str, str]]:
    """Yield ``(segment, ending)`` pairs for *text*.

    The final segment may have an empty *ending* if the text does not end
    with a line terminator.  Segments never contain line terminators.
    """
    start = 0
    i = 0
    length = len(text)
    while i < length:
        ch = text[i]
        if ch == "\r":
            if i + 1 < length and text[i + 1] == "\n":
                yield text[start:i], "\r\n"
                i += 2
            else:
                yield text[start:i], "\r"
                i += 1
            start = i
        elif ch == "\n":
            yield text[start:i], "\n"
            i += 1
            start = i
        elif ch == "\u2028":
            yield text[start:i], "\u2028"
            i += 1
            start = i
        else:
            i += 1
    if start < length:
        yield text[start:], ""


def detect_line_ending(text: str) -> LineEnding | None:
    """Return the first line ending found in *text*.

    ``None`` is returned when *text* contains no line ending.  Mixed
    endings are not an error here: the first one is reported, because a
    caller that only needs a hint (for example, to pick a default for a
    new file) does not want to scan the whole string.
    """
    for ch in text:
        if ch == "\r":
            # Look ahead for LF without materialising a slice.
            idx = text.index(ch)
            if idx + 1 < len(text) and text[idx + 1] == "\n":
                return LineEnding.CRLF
            return LineEnding.CR
        if ch == "\n":
            return LineEnding.LF
        if ch == "\u2028":
            return LineEnding.LS
    return None


def normalize(text: str, ending: LineEnding = LineEnding.LF) -> str:
    """Convert every line ending in *text* to *ending*.

    The default is LF because that is what most tools and version control
    systems expect.  Passing ``LineEnding.CRLF`` produces Windows-style
    text; the other two values are available for completeness.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    if not isinstance(ending, LineEnding):
        raise TypeError("ending must be a LineEnding")
    replacement = ending.value
    parts = []
    for segment, _ in _iter_raw_segments(text):
        parts.append(segment)
    result = replacement.join(parts)
    if text and text[-1] in ("\r", "\n", "\u2028"):
        result += replacement
    return result


def split_lines(text: str) -> list[str]:
    """Split *text* on any supported line ending.

    The returned list contains the lines without their terminators.  A
    trailing terminator does not produce a trailing empty string, which
    is the behaviour most callers want when reading a file line by line.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    lines = [segment for segment, _ in _iter_raw_segments(text)]
    # ``_iter_raw_segments`` only yields a trailing empty segment when the
    # text ends with a terminator; drop it to match ``str.splitlines``.
    if lines and lines[-1] == "":
        lines.pop()
    return lines


def iter_lines(text: str) -> Iterator[str]:
    """Yield lines from *text* without their terminators.

    Unlike :func:`split_lines` this is lazy, which matters for very large
    strings.  The same trailing-terminator rule applies.
    """
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    segments = list(_iter_raw_segments(text))
    if segments and segments[-1][1] == "" and segments[-1][0] == "":
        segments.pop()
    for segment, _ in segments:
        yield segment
