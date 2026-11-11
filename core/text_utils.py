"""Преобразование и статистика текста для задания 2."""

from dataclasses import dataclass


@dataclass
class TextStats:
    """Статистика по введённому тексту."""

    chars: int
    chars_no_spaces: int
    words: int
    lines: int


MODES = {
    "as_is": "Без изменений",
    "upper": "ВЕРХНИЙ РЕГИСТР",
    "lower": "нижний регистр",
    "title": "С Заглавных Букв",
    "reverse": "Задом наперёд",
}


def transform_text(text: str, mode: str = "as_is") -> str:
    """Преобразует текст согласно выбранному режиму."""
    if mode not in MODES:
        raise ValueError(f"Неизвестный режим: {mode}")

    if mode == "upper":
        return text.upper()
    if mode == "lower":
        return text.lower()
    if mode == "title":
        return text.title()
    if mode == "reverse":
        return text[::-1]
    return text


def text_stats(text: str) -> TextStats:
    """Считает количество символов, слов и строк."""
    if text:
        lines = text.count("\n") + (0 if text.endswith("\n") else 1)
    else:
        lines = 0

    return TextStats(
        chars=len(text),
        chars_no_spaces=len(text.replace(" ", "")),
        words=len(text.split()),
        lines=lines,
    )


def format_result(text: str, mode: str = "as_is") -> str:
    """Возвращает готовую строку для вывода в интерфейсе."""
    transformed = transform_text(text, mode)
    stats = text_stats(text)
    return (
        f"Результат ({MODES[mode]}):\n{transformed}\n\n"
        f"Символов: {stats.chars}, слов: {stats.words}, строк: {stats.lines}"
    )
