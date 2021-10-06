# coding: utf-8
from __future__ import print_function

import os
import logging

from PySide2.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QWidget
)

from .utils import AppSettings
from .script_editor import NukeScriptEditor
from .connection import Server, TestClient, SendNodesClient
from .widgets import (
    LogWidgets,
    ConnectionsWidget,
    ErrorDialog,
    ToolBar
)

LOGGER = logging.getLogger('NukeServerSocket.main')
LOGGER.debug('\nSTART APPLICATION')

_TMP_FOLDER = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), '.tmp'
)
if not os.path.exists(_TMP_FOLDER):
    os.mkdir(_TMP_FOLDER)


class MainWindowWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)

        self.settings = AppSettings()
        self.settings.verify_port_config()
        self.settings.setValue(
            'path/transfer_file',
            os.path.join(_TMP_FOLDER, 'transfer_nodes.tmp')
        )

        self.log_widgets = LogWidgets()

        self.connections = ConnectionsWidget(parent=self)

        self.connect_btn = self.connections.buttons.connect_btn
        self.connect_btn.toggled.connect(self._connection)

        self.send_btn = self.connections.buttons.send_btn
        self.send_btn.clicked.connect(self._send_nodes)

        self.test_btn = self.connections.buttons.test_btn
        self.test_btn.clicked.connect(self._test_receiver)

        _layout = QVBoxLayout()
        _layout.addWidget(self.connections)
        _layout.addWidget(self.log_widgets)

        self.setLayout(_layout)

        self._server = None
        self._test_client = None
        self._node_client = None

        NukeScriptEditor.init_editor()

    def _enable_connection_mod(self, state):  # type: (bool) -> None
        """Enable/disable connection widgets modification.

        When connected the port and the sender mode will be disabled.

        Args:
            state (bool): state of the widget.
        """
        self.connections.server_port.setEnabled(state)
        self.connections.sender_mode.setEnabled(state)

    def _connection(self, state):  # type: (bool) -> None
        """When connect button is toggled start connection, otherwise close it."""

        def _start_connection():
            """Setup connection to server."""
            self._server = Server(self.log_widgets)

            try:
                status = self._server.start_server()
            except ValueError as err:
                LOGGER.error('server did not connect: %s', err)
                self.connect_btn.disconnect()
                self.connections.set_disconnected()
            else:
                LOGGER.debug('server is connected: %s', status)
                self._enable_connection_mod(False)

        if state:
            _start_connection()
        else:
            self._server.close_server()
            self._enable_connection_mod(True)

    def _send_nodes(self):
        """Send the selected Nuke Nodes using the internal client."""
        self._node_client = SendNodesClient()
        self._node_client.connect()

    def _test_receiver(self):
        """Send a test message using the internal client."""
        self._test_client = TestClient()
        self._test_client.connect()


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setWindowTitle("NukeServerSocket")

        toolbar = ToolBar()
        self.addToolBar(toolbar)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        try:
            main_window = MainWindowWidget(self)
        except Exception as err:
            ErrorDialog(err, self).show()
            LOGGER.critical(err, exc_info=True)
        else:
            self.setCentralWidget(main_window)


try:
    import nukescripts
except ImportError as error:
    pass
else:
    nukescripts.panels.registerWidgetAsPanel(
        'NukeServerSocket.src.main.MainWindow', 'NukeServerSocket',
        'NukeServerSocket.MainWindow')
