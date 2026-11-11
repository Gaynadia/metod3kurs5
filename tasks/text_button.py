"""Задание 2 (средняя сложность): окно с текстовым полем и кнопкой."""

import os
import sys
import tkinter as tk
from tkinter import messagebox, ttk

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.text_utils import MODES, format_result


class TextButtonApp(tk.Tk):
    """Окно: пользователь вводит текст, кнопка выводит результат."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Задание 2 — текстовое поле и кнопка")
        self.geometry("540x430")
        self.resizable(False, False)
        self.configure(bg="#f4f6fb")
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(
            self,
            text="Введите текст и нажмите кнопку",
            font=("Segoe UI", 14, "bold"),
            bg="#f4f6fb",
            fg="#2c3e50",
        ).pack(pady=(18, 8))

        self.entry = tk.Entry(self, font=("Segoe UI", 12), width=44)
        self.entry.pack(pady=6)
        self.entry.insert(0, "Привет, мир!")

        mode_frame = tk.Frame(self, bg="#f4f6fb")
        mode_frame.pack(pady=6)
        tk.Label(
            mode_frame, text="Режим:", bg="#f4f6fb", font=("Segoe UI", 10)
        ).pack(side=tk.LEFT, padx=4)

        self.mode_var = tk.StringVar(value="as_is")
        ttk.Combobox(
            mode_frame,
            textvariable=self.mode_var,
            values=list(MODES.keys()),
            state="readonly",
            width=18,
        ).pack(side=tk.LEFT)

        tk.Button(
            self,
            text="Показать текст",
            command=self.show_text,
            font=("Segoe UI", 11, "bold"),
            bg="#2ecc71",
            fg="white",
            activebackground="#27ae60",
            activeforeground="white",
            padx=18,
            pady=6,
            relief=tk.FLAT,
        ).pack(pady=12)

        self.result = tk.Label(
            self,
            text="Здесь появится результат…",
            font=("Consolas", 10),
            bg="white",
            fg="#34495e",
            justify=tk.LEFT,
            anchor="nw",
            wraplength=480,
            relief=tk.SOLID,
            bd=1,
            padx=10,
            pady=10,
        )
        self.result.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 18))

    def show_text(self) -> None:
        """Показывает введённый текст в выбранном режиме."""
        text = self.entry.get()
        if not text.strip():
            messagebox.showwarning("Пусто", "Сначала введите текст.")
            return
        self.result.config(text=format_result(text, self.mode_var.get()))


def run_text_button() -> None:
    """Запускает приложение задания 2."""
    TextButtonApp().mainloop()


if __name__ == "__main__":
    run_text_button()
