"""Чтение файла и предпросмотр для задания 8."""

import os
from dataclasses import dataclass


@dataclass
class FilePreview:
    """Краткая информация о выбранном файле и его начало."""

    path: str
    name: str
    size: int
    total_lines: int
    text: str
    truncated: bool

    @property
    def size_kb(self) -> float:
        """Размер файла в килобайтах."""
        return round(self.size / 1024, 2)


def read_preview(path: str, max_chars: int = 1000) -> FilePreview:
    """Читает начало текстового файла и собирает информацию о нём."""
    if max_chars <= 0:
        raise ValueError("max_chars должен быть положительным")

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Файл не найден: {path}")

    with open(path, "r", encoding="utf-8", errors="replace") as file:
        content = file.read()

    if not content:
        total_lines = 0
    elif content.endswith("\n"):
        total_lines = content.count("\n")
    else:
        total_lines = content.count("\n") + 1

    return FilePreview(
        path=os.path.abspath(path),
        name=os.path.basename(path),
        size=os.path.getsize(path),
        total_lines=total_lines,
        text=content[:max_chars],
        truncated=len(content) > max_chars,
    )
