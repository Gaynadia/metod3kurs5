"""Задание 8 (средняя сложность): диалог выбора файла."""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.file_utils import read_preview


class FileDialogApp(tk.Tk):
    """Окно с кнопкой выбора файла и предпросмотром его содержимого."""

    PREVIEW_CHARS = 1500

    def __init__(self) -> None:
        super().__init__()
        self.title("Задание 8 — диалог выбора файла")
        self.geometry("620x460")
        self.configure(bg="#f4f6fb")
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(
            self,
            text="Выберите текстовый файл для предпросмотра",
            font=("Segoe UI", 13, "bold"),
            bg="#f4f6fb",
            fg="#2c3e50",
        ).pack(pady=(18, 8))

        self.path_var = tk.StringVar(value="Файл не выбран")
        tk.Label(
            self,
            textvariable=self.path_var,
            font=("Consolas", 9),
            bg="#f4f6fb",
            fg="#7f8c8d",
            wraplength=560,
            justify=tk.LEFT,
        ).pack(pady=4)

        self.info_var = tk.StringVar(value="")
        tk.Label(
            self,
            textvariable=self.info_var,
            font=("Segoe UI", 10),
            bg="#f4f6fb",
            fg="#2980b9",
        ).pack(pady=4)

        tk.Button(
            self,
            text="Выбрать файл…",
            command=self.choose_file,
            font=("Segoe UI", 11, "bold"),
            bg="#9b59b6",
            fg="white",
            activebackground="#8e44ad",
            activeforeground="white",
            padx=18,
            pady=6,
            relief=tk.FLAT,
        ).pack(pady=10)

        self.content = tk.Text(
            self,
            height=14,
            width=70,
            font=("Consolas", 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.SOLID,
            bd=1,
        )
        self.content.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 18))
        self._set_content("Здесь появится содержимое выбранного файла…")

    def _set_content(self, text: str) -> None:
        self.content.config(state=tk.NORMAL)
        self.content.delete("1.0", tk.END)
        self.content.insert(tk.END, text)
        self.content.config(state=tk.DISABLED)

    def choose_file(self) -> None:
        """Открывает диалог выбора файла и показывает предпросмотр."""
        path = filedialog.askopenfilename(
            title="Выберите текстовый файл",
            filetypes=[
                ("Текстовые файлы", "*.txt"),
                ("Python", "*.py"),
                ("Все файлы", "*.*"),
            ],
        )
        if not path:
            return

        try:
            preview = read_preview(path, max_chars=self.PREVIEW_CHARS)
        except OSError as error:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл:\n{error}")
            return

        self.path_var.set(preview.path)
        note = (
            f"Размер: {preview.size_kb} КБ  |  строк: {preview.total_lines}"
        )
        if preview.truncated:
            note += f"  |  показаны первые {self.PREVIEW_CHARS} символов"
        self.info_var.set(note)
        self._set_content(preview.text)


def run_file_dialog() -> None:
    """Запускает приложение задания 8."""
    FileDialogApp().mainloop()


if __name__ == "__main__":
    run_file_dialog()
