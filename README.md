# py_universal_line_ending_normalizer

Detects and converts between CR, LF, CRLF, and the Unicode line separator
(U+2028) on strings.

```python
from py_universal_line_ending_normalizer import (
    LineEnding,
    detect_line_ending,
    normalize,
    split_lines,
    iter_lines,
)

text = "first\r\nsecond\rthird\u2028fourth"
print(detect_line_ending(text))   # LineEnding.CRLF
print(normalize(text))            # first\nsecond\nthird\nfourth
print(normalize(text, LineEnding.CRLF))
print(split_lines(text))          # ['first', 'second', 'third', 'fourth']
print(list(iter_lines(text)))     # ['first', 'second', 'third', 'fourth']
```

## Why this exists

Text that moves between Windows, Unix, classic Mac OS, and Unicode-aware
tools accumulates four different line terminators.  A normalizer that
only knows about LF and CRLF will corrupt a file that uses bare CR, and a
normalizer that treats CR as ordinary whitespace will silently join lines
in files that have no LF at all.

The trade-off made here is that a bare CR is always a line ending.  That
is the only rule that lets a CR-only file round-trip correctly.  The cost
is that a literal CR inside a field (rare, but legal in some formats) is
interpreted as a break; callers who need to preserve such a CR must keep
it out of the text handed to this library.

## API

- `LineEnding` — enum with members `CR`, `LF`, `CRLF`, and `LS`.
- `detect_line_ending(text)` — returns the first `LineEnding` found, or
  `None` if the string contains no line ending.
- `normalize(text, ending=LineEnding.LF)` — returns a new string with
  every line ending replaced by `ending`.  Raises `TypeError` for
  non-string input or a non-`LineEnding` target.
- `split_lines(text)` — returns a list of lines without terminators.  A
  trailing terminator does not add a final empty string.
- `iter_lines(text)` — lazy version of `split_lines`.

## The awkward edge

Mixed endings are not an error.  `detect_line_ending` reports only the
first one it sees, so a string that starts with CRLF and later contains LF
is reported as CRLF.  That is deliberate: detection is a hint, not a
validation.  If you need to know whether a string is internally
consistent, compare `detect_line_ending` against the endings in
`split_lines` output yourself.
