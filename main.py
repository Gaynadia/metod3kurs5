"""Лаунчер лабораторной работы № 5 (вариант 10).

Каждое задание запускается отдельным процессом, чтобы окна Tkinter и PyQt5
не мешали друг другу.
"""

import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TASKS = [
    ("Средняя № 10 — простой GUI на PyQt5", "tasks.pyqt_hello"),
    ("Средняя № 2 — текст и кнопка", "tasks.text_button"),
    ("Средняя № 8 — диалог выбора файла", "tasks.file_dialog"),
    ("Повышенная № 10 — локальный чат", "tasks.local_chat"),
    ("Повышенная № 3 — игра «Кликер»", "tasks.clicker_game"),
]


class LauncherApp(tk.Tk):
    """Окно-меню со списком заданий."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Лабораторная работа № 5 — вариант 10")
        self.geometry("560x470")
        self.resizable(False, False)
        self.configure(bg="#1f2a44")
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(
            self,
            text="Визуальное программирование на Python",
            font=("Segoe UI", 15, "bold"),
            bg="#1f2a44",
            fg="white",
        ).pack(pady=(22, 4))

        tk.Label(
            self,
            text="Лабораторная № 5 · вариант 10 · Мешавкин Алексей",
            font=("Segoe UI", 9),
            bg="#1f2a44",
            fg="#9fb3d1",
        ).pack(pady=(0, 16))

        for title, module in TASKS:
            tk.Button(
                self,
                text=title,
                command=lambda m=module: self.launch(m),
                font=("Segoe UI", 11),
                bg="#2f80ed",
                fg="white",
                activebackground="#1c6fd6",
                activeforeground="white",
                relief=tk.FLAT,
                anchor="w",
                padx=16,
                pady=8,
            ).pack(fill=tk.X, padx=28, pady=4)

        tk.Button(
            self,
            text="Проверить тесты (unittest)",
            command=self.run_tests,
            font=("Segoe UI", 10, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#1e8449",
            activeforeground="white",
            relief=tk.FLAT,
            pady=7,
        ).pack(fill=tk.X, padx=28, pady=(16, 4))

        tk.Button(
            self,
            text="Выход",
            command=self.destroy,
            font=("Segoe UI", 10),
            bg="#4a5873",
            fg="white",
            activebackground="#3a4559",
            activeforeground="white",
            relief=tk.FLAT,
            pady=6,
        ).pack(fill=tk.X, padx=28, pady=(4, 20))

    def launch(self, module: str) -> None:
        """Запускает задание в отдельном процессе."""
        try:
            subprocess.Popen([sys.executable, "-m", module], cwd=BASE_DIR)
        except OSError as error:
            messagebox.showerror("Ошибка запуска", str(error))

    def run_tests(self) -> None:
        """Запускает unit-тесты и показывает результат."""
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-v"],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
        )
        output = (result.stderr or result.stdout).strip()
        tail = output[-2500:]

        if result.returncode == 0:
            messagebox.showinfo("Тесты", "Все тесты пройдены.\n\n" + tail)
        else:
            messagebox.showerror("Тесты", "Есть ошибки.\n\n" + tail)


def console_menu() -> None:
    """Запасное текстовое меню, если окно Tkinter недоступно."""
    print("=" * 62)
    print("  ЛАБОРАТОРНАЯ РАБОТА № 5: ВИЗУАЛЬНОЕ ПРОГРАММИРОВАНИЕ")
    print("  Вариант 10 · Мешавкин Алексей")
    print("=" * 62)
    for index, (title, module) in enumerate(TASKS, start=1):
        print(f"  [{index}] {title}  ({module})")
    print("  [0] Выход")
    print("-" * 62)

    while True:
        choice = input("Номер задания (0-5): ").strip()
        if choice == "0":
            print("Выход.")
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(TASKS):
            print("Неверный выбор.")
            continue

        module = TASKS[int(choice) - 1][1]
        subprocess.Popen([sys.executable, "-m", module], cwd=BASE_DIR)


def main() -> None:
    if "--cli" in sys.argv:
        console_menu()
        return

    try:
        LauncherApp().mainloop()
    except tk.TclError:
        console_menu()


if __name__ == "__main__":
    main()
