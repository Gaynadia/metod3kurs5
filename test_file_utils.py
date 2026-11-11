"""Тесты чтения файла и предпросмотра (задание 8)."""

import os
import tempfile
import unittest

from core.file_utils import read_preview


class TestReadPreview(unittest.TestCase):
    """Проверка чтения файла и собранной статистики."""

    def setUp(self):
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".txt", delete=False, encoding="utf-8"
        )
        handle.write("Первая строка\nВторая строка\n")
        handle.close()
        self.path = handle.name

    def tearDown(self):
        if os.path.exists(self.path):
            os.unlink(self.path)

    def test_reads_content(self):
        preview = read_preview(self.path)
        self.assertIn("Первая строка", preview.text)
        self.assertEqual(preview.name, os.path.basename(self.path))
        self.assertFalse(preview.truncated)

    def test_counts_lines(self):
        preview = read_preview(self.path)
        self.assertEqual(preview.total_lines, 2)

    def test_truncates_long_text(self):
        preview = read_preview(self.path, max_chars=5)
        self.assertTrue(preview.truncated)
        self.assertEqual(preview.text, "Перва")

    def test_size_is_positive(self):
        preview = read_preview(self.path)
        self.assertGreater(preview.size, 0)
        self.assertGreaterEqual(preview.size_kb, 0)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            read_preview("файла_точно_нет_12345.txt")

    def test_invalid_max_chars(self):
        with self.assertRaises(ValueError):
            read_preview(self.path, max_chars=0)


if __name__ == "__main__":
    unittest.main()
