import unittest

from py_universal_line_ending_normalizer import (
    LineEnding,
    detect_line_ending,
    normalize,
    split_lines,
    iter_lines,
)


class DetectTests(unittest.TestCase):
    def test_detects_lf(self):
        self.assertEqual(detect_line_ending("a\nb"), LineEnding.LF)

    def test_detects_crlf(self):
        self.assertEqual(detect_line_ending("a\r\nb"), LineEnding.CRLF)

    def test_detects_cr(self):
        self.assertEqual(detect_line_ending("a\rb"), LineEnding.CR)

    def test_detects_ls(self):
        self.assertEqual(detect_line_ending("a\u2028b"), LineEnding.LS)

    def test_returns_none_when_no_ending(self):
        self.assertIsNone(detect_line_ending("plain text"))

    def test_returns_first_ending_in_mixed_text(self):
        self.assertEqual(detect_line_ending("a\r\nb\nc"), LineEnding.CRLF)
        self.assertEqual(detect_line_ending("a\nb\r\nc"), LineEnding.LF)

    def test_crlf_is_not_reported_as_cr(self):
        self.assertEqual(detect_line_ending("x\r\n"), LineEnding.CRLF)


class NormalizeTests(unittest.TestCase):
    def test_default_is_lf(self):
        self.assertEqual(normalize("a\r\nb\rc\u2028d"), "a\nb\nc\nd")

    def test_to_crlf(self):
        self.assertEqual(normalize("a\nb\rc", LineEnding.CRLF), "a\r\nb\r\nc")

    def test_to_cr(self):
        self.assertEqual(normalize("a\r\nb\nc", LineEnding.CR), "a\rb\rc")

    def test_to_ls(self):
        self.assertEqual(normalize("a\r\nb\rc", LineEnding.LS), "a\u2028b\u2028c")

    def test_preserves_trailing_terminator(self):
        self.assertEqual(normalize("a\r\n"), "a\n")

    def test_empty_string(self):
        self.assertEqual(normalize(""), "")

    def test_rejects_non_string(self):
        with self.assertRaises(TypeError):
            normalize(b"bytes")

    def test_rejects_non_enum_ending(self):
        with self.assertRaises(TypeError):
            normalize("a\n", "\n")


class SplitLinesTests(unittest.TestCase):
    def test_splits_mixed_endings(self):
        self.assertEqual(split_lines("a\r\nb\rc\nd"), ["a", "b", "c", "d"])

    def test_trailing_terminator_does_not_produce_empty_line(self):
        self.assertEqual(split_lines("a\n"), ["a"])

    def test_empty_string(self):
        self.assertEqual(split_lines(""), [])

    def test_leading_terminator_produces_empty_first_line(self):
        self.assertEqual(split_lines("\na"), ["", "a"])

    def test_rejects_non_string(self):
        with self.assertRaises(TypeError):
            split_lines(123)


class IterLinesTests(unittest.TestCase):
    def test_yields_lines_lazily(self):
        self.assertEqual(list(iter_lines("a\r\nb\rc\nd")), ["a", "b", "c", "d"])

    def test_trailing_terminator_does_not_produce_empty_line(self):
        self.assertEqual(list(iter_lines("a\n")), ["a"])

    def test_empty_string(self):
        self.assertEqual(list(iter_lines("")), [])

    def test_rejects_non_string(self):
        with self.assertRaises(TypeError):
            list(iter_lines(None))


if __name__ == "__main__":
    unittest.main()
