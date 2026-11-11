"""Задание 10 (средняя сложность): простейший GUI на PyQt5."""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PyQtHelloWindow(QWidget):
    """Небольшое окно PyQt5 с меткой и кнопкой."""

    def __init__(self) -> None:
        super().__init__()
        self._clicks = 0
        self.setWindowTitle("Задание 10 — PyQt5")
        self.resize(430, 260)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout()

        self.label = QLabel("Привет из PyQt5!\nВариант 10")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "font-size: 18px; color: #2c3e50; font-weight: bold;"
        )
        layout.addWidget(self.label)

        self.button = QPushButton("Нажми меня")
        self.button.setStyleSheet(
            "QPushButton {"
            "  background-color: #3498db; color: white;"
            "  font-size: 14px; padding: 10px; border-radius: 6px;"
            "}"
            "QPushButton:hover { background-color: #2980b9; }"
        )
        self.button.clicked.connect(self.on_click)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def on_click(self) -> None:
        """Обработчик нажатия кнопки."""
        self._clicks += 1
        self.label.setText(
            f"Привет из PyQt5!\nВариант 10\nНажатий: {self._clicks}"
        )


def run_pyqt_hello() -> None:
    """Запускает приложение PyQt5."""
    app = QApplication.instance() or QApplication(sys.argv)
    window = PyQtHelloWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    run_pyqt_hello()
