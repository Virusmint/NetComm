import sys
import os
import asyncio
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
import qasync

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.client import ClientCore
from widgets.chat_window import ChatWindow
from widgets.connect_dialog import ConnectDialog

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class ChatApplication(QObject):
    message_received = pyqtSignal(str)
    connection_status = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.client = None
        self.chat_window = ChatWindow()

        self.setup_connections()
        self.chat_window.show()
        self.show_connect_dialog()

    def setup_connections(self):
        self.chat_window.message_sent.connect(self.handle_send_message)
        self.chat_window.disconnect_requested.connect(self.disconnect)
        self.chat_window.window_closing.connect(self.handle_window_close)
        self.message_received.connect(self.chat_window.add_message)
        self.connection_status.connect(self.chat_window.set_connected)

    def handle_send_message(self, message: str):
        QTimer.singleShot(0, lambda: asyncio.ensure_future(self.send_message(message)))

    def show_connect_dialog(self):
        dialog = ConnectDialog(self.chat_window)
        dialog.connect_requested.connect(self.handle_connect_request)
        dialog.exec_()

    def handle_connect_request(self, host: str, port: int, alias: str):
        QTimer.singleShot(
            0, lambda: asyncio.ensure_future(self.connect_to_server(host, port, alias))
        )

    async def connect_to_server(self, host: str, port: int, alias: str):
        self.client = ClientCore(host, port, alias)
        self.client.set_message_callback(self.on_message_received)

        try:
            if await self.client.connect():
                self.connection_status.emit(True)
                self.chat_window.add_message(f"Connected to {host}:{port} as {alias}")
            else:
                self.connection_status.emit(False)
                QMessageBox.critical(
                    self.chat_window,
                    "Connection Error",
                    f"Failed to connect to {host}:{port}",
                )
                self.show_connect_dialog()
        except Exception as e:
            logger.error(f"Connection error: {e}")
            QMessageBox.critical(self.chat_window, "Connection Error", str(e))

    def on_message_received(self, message: str):
        self.message_received.emit(message)

    async def send_message(self, message: str):
        if self.client and self.client.connected:
            self.chat_window.add_message(f"You: {message}")
            await self.client.send_message(message)

    def disconnect(self, show_dialog=True):
        if self.client:
            self.client.close()
            self.connection_status.emit(False)
            self.chat_window.add_message("Disconnected from server")
            if show_dialog:
                self.show_connect_dialog()

    def handle_window_close(self):
        # Handle window close without showing reconnect dialog
        if self.client:
            self.client.close()
        # Exit the application
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    chat_app = ChatApplication()

    def cleanup():
        if chat_app.client:
            chat_app.client.close()

    app.aboutToQuit.connect(cleanup)

    try:
        with loop:
            loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()
