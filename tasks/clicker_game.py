"""Задание 3 (повышенная сложность): игра «Кликер»."""

import os
import sys
import time
import tkinter as tk

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.clicker import ClickerGame


class ClickerApp(tk.Tk):
    """Игра: за 10 секунд нужно успеть кликнуть как можно больше раз."""

    def __init__(self, duration: float = 10.0) -> None:
        super().__init__()
        self.title("Задание 3 — игра «Кликер»")
        self.geometry("430x380")
        self.resizable(False, False)
        self.configure(bg="#f4f6fb")

        self.game = ClickerGame(duration)
        self._last_tick = 0.0
        self._tick_job = None
        self._build_ui()

    def _build_ui(self) -> None:
        tk.Label(
            self,
            text="Успей кликнуть как можно больше за 10 секунд!",
            font=("Segoe UI", 12, "bold"),
            bg="#f4f6fb",
            fg="#2c3e50",
        ).pack(pady=(18, 10))

        self.score_label = tk.Label(
            self,
            text="Счёт: 0",
            font=("Segoe UI", 26, "bold"),
            bg="#f4f6fb",
            fg="#e74c3c",
        )
        self.score_label.pack(pady=6)

        self.timer_label = tk.Label(
            self,
            text="Осталось: 10.0 с",
            font=("Segoe UI", 12),
            bg="#f4f6fb",
            fg="#7f8c8d",
        )
        self.timer_label.pack(pady=2)

        self.cps_label = tk.Label(
            self,
            text="Кликов в секунду: 0.0",
            font=("Segoe UI", 10),
            bg="#f4f6fb",
            fg="#7f8c8d",
        )
        self.cps_label.pack(pady=2)

        self.click_button = tk.Button(
            self,
            text="КЛИК!",
            command=self.on_click,
            font=("Segoe UI", 18, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            width=12,
            height=2,
            state=tk.DISABLED,
        )
        self.click_button.pack(pady=14)

        self.start_button = tk.Button(
            self,
            text="Старт игры",
            command=self.start_game,
            font=("Segoe UI", 12, "bold"),
            bg="#2ecc71",
            fg="white",
            activebackground="#27ae60",
            activeforeground="white",
            padx=16,
            pady=5,
            relief=tk.FLAT,
        )
        self.start_button.pack(pady=4)

        self.status_label = tk.Label(
            self,
            text="Нажмите «Старт игры»",
            font=("Segoe UI", 10, "italic"),
            bg="#f4f6fb",
            fg="#7f8c8d",
        )
        self.status_label.pack(pady=6)

    def start_game(self) -> None:
        """Сбрасывает и запускает новый раунд."""
        self.game.start()
        self._last_tick = time.monotonic()
        self.click_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.DISABLED)
        self.status_label.config(text="Игра началась — кликайте!")
        self._refresh()
        self._tick_job = self.after(100, self._tick)

    def on_click(self) -> None:
        """Обрабатывает клик по кнопке."""
        self.game.click()
        self._refresh()

    def _tick(self) -> None:
        self._tick_job = None
        now = time.monotonic()
        delta = now - self._last_tick
        self._last_tick = now

        active = self.game.update(delta)
        self._refresh()

        if active:
            self._tick_job = self.after(100, self._tick)
            return

        self.click_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        self.status_label.config(
            text=(
                f"Время вышло! Счёт: {self.game.score}. "
                f"Рекорд: {self.game.best_score}"
            )
        )

    def destroy(self) -> None:
        if self._tick_job is not None:
            try:
                self.after_cancel(self._tick_job)
            except tk.TclError:
                pass
            self._tick_job = None
        super().destroy()

    def _refresh(self) -> None:
        self.score_label.config(text=f"Счёт: {self.game.score}")
        self.timer_label.config(text=f"Осталось: {self.game.time_left:4.1f} с")
        self.cps_label.config(
            text=f"Кликов в секунду: {self.game.clicks_per_second:.1f}"
        )


def run_clicker_game() -> None:
    """Запускает игру «Кликер»."""
    ClickerApp().mainloop()


if __name__ == "__main__":
    run_clicker_game()
