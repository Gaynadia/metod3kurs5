"""Задание 10 (повышенная сложность): локальный чат по TCP."""

import os
import queue
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from core.chat import ChatClient, ChatServer


class LocalChatApp(tk.Tk):
    """Окно чата: можно поднять сервер и подключиться к нему.

    Чтобы проверить чат, запустите второе окно приложения и подключитесь
    к тому же хосту и порту — сообщения будут видны в обоих окнах.
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("Задание 10 — локальный чат")
        self.geometry("680x540")
        self.minsize(600, 460)
        self.configure(bg="#f4f6fb")

        self.server = None
        self.client = None
        self.events = queue.Queue()
        self._events_job = None

        self._build_ui()
        self._events_job = self.after(100, self._process_events)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        settings = tk.Frame(self, bg="#f4f6fb")
        settings.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(settings, text="Хост:", bg="#f4f6fb").grid(
            row=0, column=0, sticky="w"
        )
        self.host_var = tk.StringVar(value="127.0.0.1")
        tk.Entry(settings, textvariable=self.host_var, width=13).grid(
            row=0, column=1, padx=4
        )

        tk.Label(settings, text="Порт:", bg="#f4f6fb").grid(row=0, column=2)
        self.port_var = tk.StringVar(value="8765")
        tk.Entry(settings, textvariable=self.port_var, width=7).grid(
            row=0, column=3, padx=4
        )

        tk.Label(settings, text="Имя:", bg="#f4f6fb").grid(row=0, column=4)
        self.name_var = tk.StringVar(value="Пользователь")
        tk.Entry(settings, textvariable=self.name_var, width=15).grid(
            row=0, column=5, padx=4
        )

        self.server_button = tk.Button(
            settings,
            text="Запустить сервер",
            command=self.start_server,
            bg="#9b59b6",
            fg="white",
            activebackground="#8e44ad",
            activeforeground="white",
            relief=tk.FLAT,
            padx=8,
        )
        self.server_button.grid(row=0, column=6, padx=(10, 4))

        self.connect_button = tk.Button(
            settings,
            text="Подключиться",
            command=self.toggle_connection,
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            relief=tk.FLAT,
            padx=8,
        )
        self.connect_button.grid(row=0, column=7, padx=4)

        self.status_label = tk.Label(
            self,
            text="Сервер не запущен, клиент не подключён",
            bg="#f4f6fb",
            fg="#7f8c8d",
            anchor="w",
        )
        self.status_label.pack(fill=tk.X, padx=12)

        self.chat_log = scrolledtext.ScrolledText(
            self,
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            bd=1,
        )
        self.chat_log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        bottom = tk.Frame(self, bg="#f4f6fb")
        bottom.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.message_entry = tk.Entry(bottom, font=("Segoe UI", 11))
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.message_entry.bind("<Return>", lambda event: self.send_message())
        self.message_entry.config(state=tk.DISABLED)

        tk.Button(
            bottom,
            text="Отправить",
            command=self.send_message,
            bg="#2ecc71",
            fg="white",
            activebackground="#27ae60",
            activeforeground="white",
            relief=tk.FLAT,
            padx=12,
        ).pack(side=tk.RIGHT, padx=(8, 0))

        self._append_system("Введите имя, при необходимости запустите сервер "
                            "и нажмите «Подключиться».")

    def _read_port(self) -> int:
        try:
            port = int(self.port_var.get())
        except ValueError:
            raise ValueError("Порт должен быть целым числом") from None

        if not 1 <= port <= 65535:
            raise ValueError("Порт должен быть в диапазоне 1..65535")
        return port

    def _append_line(self, line: str) -> None:
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, line + "\n")
        self.chat_log.config(state=tk.DISABLED)
        self.chat_log.see(tk.END)

    def _append_system(self, text: str) -> None:
        self._append_line(f"* {text}")

    def start_server(self) -> None:
        """Поднимает локальный сервер в фоновом потоке."""
        if self.server is not None and self.server.running:
            messagebox.showinfo("Сервер", "Сервер уже запущен.")
            return

        try:
            server = ChatServer(self.host_var.get().strip(), self._read_port())
            server.on_log = lambda text: self.events.put(("system", text))
            server.start()
        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Сервер", f"Не удалось запустить сервер:\n{error}"
            )
            return

        self.server = server
        self.server_button.config(state=tk.DISABLED)
        self.status_label.config(
            text=f"Сервер слушает {server.host}:{server.port}"
        )
        self._append_system(f"Сервер запущен на {server.host}:{server.port}")

    def toggle_connection(self) -> None:
        """Подключается к серверу или отключается от него."""
        if self.client is not None and self.client.connected:
            self.disconnect_client()
            return

        name = self.name_var.get().strip() or "Гость"
        try:
            client = ChatClient(
                self.host_var.get().strip(), self._read_port()
            )
        except ValueError as error:
            messagebox.showerror("Подключение", str(error))
            return

        client.on_message = lambda message: self.events.put(
            ("message", message)
        )
        client.on_disconnect = lambda: self.events.put(("disconnected", None))

        try:
            client.connect(name)
        except OSError as error:
            messagebox.showerror(
                "Подключение", f"Не удалось подключиться:\n{error}"
            )
            return

        self.client = client
        self.connect_button.config(text="Отключиться")
        self.message_entry.config(state=tk.NORMAL)
        self.message_entry.focus_set()
        self.status_label.config(text=f"Подключено как «{name}»")
        self._append_system(f"Вы подключились как «{name}»")

    def disconnect_client(self) -> None:
        """Отключает клиент от сервера."""
        if self.client is not None:
            self.client.disconnect()
            self.client = None

        self.connect_button.config(text="Подключиться")
        self.message_entry.config(state=tk.DISABLED)
        self.status_label.config(text="Клиент отключён")
        self._append_system("Вы отключились от чата")

    def send_message(self) -> None:
        """Отправляет введённое сообщение на сервер."""
        text = self.message_entry.get().strip()
        if not text:
            return

        if self.client is None or not self.client.connected:
            messagebox.showwarning(
                "Чат", "Сначала подключитесь к серверу."
            )
            return

        try:
            self.client.send(text)
        except (OSError, ConnectionError) as error:
            messagebox.showerror(
                "Чат", f"Не удалось отправить сообщение:\n{error}"
            )
            return

        self.message_entry.delete(0, tk.END)

    def _process_events(self) -> None:
        """Переносит события из фоновых потоков в интерфейс Tkinter."""
        self._events_job = None
        try:
            while True:
                kind, payload = self.events.get_nowait()
                if kind == "message":
                    self._append_line(payload.format())
                elif kind == "system":
                    self._append_system(payload)
                elif kind == "disconnected":
                    self._handle_lost_connection()
        except queue.Empty:
            pass

        self._events_job = self.after(100, self._process_events)

    def _handle_lost_connection(self) -> None:
        self.client = None
        self.connect_button.config(text="Подключиться")
        self.message_entry.config(state=tk.DISABLED)
        self.status_label.config(text="Соединение с сервером потеряно")
        self._append_system("Соединение с сервером потеряно")

    def _on_close(self) -> None:
        if self.client is not None:
            self.client.disconnect()
        if self.server is not None:
            self.server.stop()
        self.destroy()

    def destroy(self) -> None:
        if self._events_job is not None:
            try:
                self.after_cancel(self._events_job)
            except tk.TclError:
                pass
            self._events_job = None
        super().destroy()


def run_local_chat() -> None:
    """Запускает приложение локального чата."""
    LocalChatApp().mainloop()


if __name__ == "__main__":
    run_local_chat()
