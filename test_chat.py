"""Тесты логики и транспорта локального чата (задание 10 повышенной сложности)."""

import threading
import time
import unittest

from core.chat import ChatClient, ChatMessage, ChatRoom, ChatServer


class TestChatMessage(unittest.TestCase):
    """Проверка сериализации и форматирования сообщения."""

    def test_json_roundtrip(self):
        message = ChatMessage(sender="Аня", text="Привет", timestamp=123.5)
        restored = ChatMessage.from_json(message.to_json())

        self.assertEqual(restored.sender, "Аня")
        self.assertEqual(restored.text, "Привет")
        self.assertEqual(restored.timestamp, 123.5)

    def test_format_contains_sender_and_text(self):
        message = ChatMessage(sender="Боб", text="Как дела?", timestamp=0)
        line = message.format()

        self.assertIn("Боб", line)
        self.assertIn("Как дела?", line)

    def test_from_json_rejects_non_object(self):
        with self.assertRaises(ValueError):
            ChatMessage.from_json('"просто строка"')


class TestChatRoom(unittest.TestCase):
    """Проверка истории сообщений."""

    def test_add_and_history(self):
        room = ChatRoom()
        room.add(ChatMessage(sender="A", text="1", timestamp=0))
        room.add(ChatMessage(sender="B", text="2", timestamp=0))

        self.assertEqual(len(room), 2)
        self.assertEqual(len(room.history_lines()), 2)

    def test_clear(self):
        room = ChatRoom()
        room.add(ChatMessage(sender="A", text="1"))
        room.clear()
        self.assertEqual(len(room), 0)


class TestChatTransport(unittest.TestCase):
    """Интеграционная проверка сервера и клиентов на localhost."""

    def setUp(self):
        self.server = ChatServer(port=0)
        self.server.start()
        self.clients = []

    def tearDown(self):
        for client in self.clients:
            client.disconnect()
        self.server.stop()

    @staticmethod
    def _wait_for(predicate, timeout=5.0):
        deadline = time.time() + timeout
        while time.time() < deadline:
            if predicate():
                return True
            time.sleep(0.02)
        return False

    @staticmethod
    def _make_handler(store, event):
        def handler(message):
            store.append(message)
            event.set()

        return handler

    def test_message_is_delivered_to_all_clients(self):
        received_first = []
        received_second = []
        first_event = threading.Event()
        second_event = threading.Event()

        first = ChatClient(port=self.server.port)
        first.on_message = self._make_handler(received_first, first_event)
        second = ChatClient(port=self.server.port)
        second.on_message = self._make_handler(received_second, second_event)
        self.clients.extend([first, second])

        first.connect("Аня")
        second.connect("Боб")

        self.assertTrue(
            self._wait_for(lambda: self.server.client_count == 2)
        )

        first.send("Привет всем!")

        self.assertTrue(first_event.wait(5.0))
        self.assertTrue(second_event.wait(5.0))
        self.assertEqual(received_first[-1].text, "Привет всем!")
        self.assertEqual(received_second[-1].text, "Привет всем!")
        self.assertEqual(received_second[-1].sender, "Аня")

    def test_send_without_connection_raises(self):
        client = ChatClient(port=1)
        with self.assertRaises(ConnectionError):
            client.send("сообщение")


if __name__ == "__main__":
    unittest.main()
