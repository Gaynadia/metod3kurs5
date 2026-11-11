"""Локальный чат по TCP-сокетам (задание 10 повышенной сложности).

Модуль разделён на две части:

* ``ChatMessage`` и ``ChatRoom`` — чистая логика, которую удобно тестировать;
* ``ChatServer`` и ``ChatClient`` — обмен сообщениями по localhost.
"""

import json
import socket
import threading
import time
from dataclasses import asdict, dataclass, field
from typing import Callable, List, Optional


@dataclass
class ChatMessage:
    """Одно сообщение чата."""

    sender: str
    text: str
    timestamp: float = field(default_factory=time.time)
    kind: str = "message"

    def to_json(self) -> str:
        """Сериализует сообщение в строку JSON."""
        return json.dumps(asdict(self), ensure_ascii=False)

    @classmethod
    def from_json(cls, raw: str) -> "ChatMessage":
        """Восстанавливает сообщение из строки JSON."""
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("Сообщение должно быть JSON-объектом")

        return cls(
            sender=str(data.get("sender", "")),
            text=str(data.get("text", "")),
            timestamp=float(data.get("timestamp", time.time())),
            kind=str(data.get("kind", "message")),
        )

    def format(self) -> str:
        """Строка для вывода в окне чата."""
        moment = time.strftime("%H:%M:%S", time.localtime(self.timestamp))
        if self.kind == "system":
            return f"[{moment}] * {self.text}"
        return f"[{moment}] {self.sender}: {self.text}"


class ChatRoom:
    """Потокобезопасная история сообщений."""

    def __init__(self) -> None:
        self._messages: List[ChatMessage] = []
        self._lock = threading.Lock()

    def add(self, message: ChatMessage) -> None:
        """Добавляет сообщение в историю."""
        with self._lock:
            self._messages.append(message)

    def all(self) -> List[ChatMessage]:
        """Возвращает копию списка сообщений."""
        with self._lock:
            return list(self._messages)

    def history_lines(self) -> List[str]:
        """Возвращает историю в виде готовых строк."""
        return [message.format() for message in self.all()]

    def clear(self) -> None:
        """Очищает историю."""
        with self._lock:
            self._messages.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._messages)


class ChatServer:
    """Простой широковещательный сервер для локального чата."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self.room = ChatRoom()
        self.on_log: Optional[Callable[[str], None]] = None

        self._socket: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False
        self._clients: List[socket.socket] = []
        self._clients_lock = threading.Lock()

    @property
    def running(self) -> bool:
        """Запущен ли сервер."""
        return self._running

    @property
    def client_count(self) -> int:
        """Количество подключённых клиентов."""
        with self._clients_lock:
            return len(self._clients)

    def start(self) -> None:
        """Занимает порт и запускает поток приёма подключений."""
        if self._running:
            return

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(8)

        self._socket = server_socket
        self.port = server_socket.getsockname()[1]
        self._running = True
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._thread.start()
        self._log(f"Сервер запущен на {self.host}:{self.port}")

    def _log(self, text: str) -> None:
        if self.on_log:
            self.on_log(text)

    def _accept_loop(self) -> None:
        while self._running and self._socket is not None:
            try:
                connection, address = self._socket.accept()
            except OSError:
                break

            threading.Thread(
                target=self._handle_client,
                args=(connection, address),
                daemon=True,
            ).start()

    def _handle_client(self, connection: socket.socket, address) -> None:
        with self._clients_lock:
            self._clients.append(connection)
        self._log(f"Подключился клиент {address[0]}:{address[1]}")

        try:
            for message in self.room.all():
                connection.sendall((message.to_json() + "\n").encode("utf-8"))

            buffer = b""
            while self._running:
                chunk = connection.recv(4096)
                if not chunk:
                    break
                buffer += chunk

                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if not line.strip():
                        continue
                    message = ChatMessage.from_json(line.decode("utf-8"))
                    self.room.add(message)
                    self._broadcast(line.decode("utf-8"))
        except (OSError, ValueError) as error:
            self._log(f"Ошибка клиента: {error}")
        finally:
            with self._clients_lock:
                if connection in self._clients:
                    self._clients.remove(connection)
            try:
                connection.close()
            except OSError:
                pass
            self._log(f"Клиент {address[0]}:{address[1]} отключился")

    def _broadcast(self, line: str) -> None:
        data = (line + "\n").encode("utf-8")
        with self._clients_lock:
            clients = list(self._clients)

        for client in clients:
            try:
                client.sendall(data)
            except OSError:
                pass

    def stop(self) -> None:
        """Останавливает сервер и закрывает все соединения."""
        self._running = False
        if self._socket is not None:
            try:
                self._socket.close()
            except OSError:
                pass

        with self._clients_lock:
            for client in self._clients:
                try:
                    client.close()
                except OSError:
                    pass
            self._clients.clear()


class ChatClient:
    """Клиент локального чата: сообщения принимаются в фоновом потоке."""

    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.host = host
        self.port = port
        self.username = "Гость"
        self.on_message: Optional[Callable[[ChatMessage], None]] = None
        self.on_disconnect: Optional[Callable[[], None]] = None

        self._socket: Optional[socket.socket] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    @property
    def connected(self) -> bool:
        """Есть ли активное соединение."""
        return self._running

    def connect(self, username: str = "Гость", timeout: float = 5.0) -> None:
        """Подключается к серверу и запускает приём сообщений."""
        if self._running:
            return

        self.username = username
        client_socket = socket.create_connection(
            (self.host, self.port), timeout=timeout
        )
        client_socket.settimeout(None)

        self._socket = client_socket
        self._running = True
        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()

    def _recv_loop(self) -> None:
        buffer = b""
        try:
            while self._running and self._socket is not None:
                chunk = self._socket.recv(4096)
                if not chunk:
                    break
                buffer += chunk

                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    if not line.strip():
                        continue
                    message = ChatMessage.from_json(line.decode("utf-8"))
                    if self.on_message:
                        self.on_message(message)
        except (OSError, ValueError):
            pass
        finally:
            self._running = False
            if self.on_disconnect:
                self.on_disconnect()

    def send(self, text: str) -> None:
        """Отправляет сообщение на сервер."""
        if not self._running or self._socket is None:
            raise ConnectionError("Клиент не подключён к серверу")

        message = ChatMessage(sender=self.username, text=text)
        self._socket.sendall((message.to_json() + "\n").encode("utf-8"))

    def disconnect(self) -> None:
        """Закрывает соединение."""
        self._running = False
        if self._socket is not None:
            try:
                self._socket.close()
            except OSError:
                pass
