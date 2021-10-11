# coding: utf-8
""" Text widget needed for status purposes."""
from __future__ import print_function

from PySide2.QtWidgets import (
    QGroupBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget
)

from ..utils import insert_time


class LogBox(QGroupBox):
    def __init__(self, title):
        QGroupBox.__init__(self, title)

        self.text_box = QPlainTextEdit()
        self.text_box.setReadOnly(True)

        btn = QPushButton('Clear log')
        btn.clicked.connect(self.text_box.clear)

        _layout = QVBoxLayout()
        _layout.addWidget(self.text_box)
        _layout.addWidget(btn)

        self.setLayout(_layout)


class LogWidgets(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.status_widget = LogBox('Status')
        self.received_widget = LogBox('Received')
        self.output_widget = LogBox('Output')

        _layout = QVBoxLayout()
        _layout.addWidget(self.status_widget)
        _layout.addWidget(self.received_widget)
        _layout.addWidget(self.output_widget)

        self.setLayout(_layout)

    @staticmethod
    def _write_log(widget, text):
        widget.text_box.insertPlainText(insert_time(text))
        widget.text_box.ensureCursorVisible()

    def set_status_text(self, text):
        self._write_log(self.status_widget, text)

    def set_received_text(self, text):
        self._write_log(self.received_widget, text)

    def set_output_text(self, text):
        text = str(text).strip()
        self._write_log(self.output_widget, text)
