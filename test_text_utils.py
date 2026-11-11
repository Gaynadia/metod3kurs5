"""Тесты преобразования и статистики текста (задание 2)."""

import unittest

from core.text_utils import format_result, text_stats, transform_text


class TestTransformText(unittest.TestCase):
    """Проверка режимов преобразования текста."""

    def test_as_is(self):
        self.assertEqual(transform_text("Привет", "as_is"), "Привет")

    def test_upper(self):
        self.assertEqual(transform_text("Привет", "upper"), "ПРИВЕТ")

    def test_lower(self):
        self.assertEqual(transform_text("ПрИвЕт", "lower"), "привет")

    def test_title(self):
        self.assertEqual(
            transform_text("привет мир", "title"), "Привет Мир"
        )

    def test_reverse(self):
        self.assertEqual(transform_text("абв", "reverse"), "вба")

    def test_unknown_mode(self):
        with self.assertRaises(ValueError):
            transform_text("текст", "unknown")


class TestTextStats(unittest.TestCase):
    """Проверка подсчёта символов, слов и строк."""

    def test_simple_sentence(self):
        stats = text_stats("привет мир")
        self.assertEqual(stats.chars, 10)
        self.assertEqual(stats.chars_no_spaces, 9)
        self.assertEqual(stats.words, 2)
        self.assertEqual(stats.lines, 1)

    def test_multiple_lines(self):
        stats = text_stats("первая\nвторая\nтретья")
        self.assertEqual(stats.lines, 3)
        self.assertEqual(stats.words, 3)

    def test_trailing_newline(self):
        self.assertEqual(text_stats("строка\n").lines, 1)

    def test_empty_text(self):
        stats = text_stats("")
        self.assertEqual(stats.chars, 0)
        self.assertEqual(stats.words, 0)
        self.assertEqual(stats.lines, 0)


class TestFormatResult(unittest.TestCase):
    """Проверка готовой строки результата."""

    def test_contains_result_and_stats(self):
        result = format_result("абв", "reverse")
        self.assertIn("вба", result)
        self.assertIn("Символов: 3", result)


if __name__ == "__main__":
    unittest.main()
