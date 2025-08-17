import sys
import asyncio
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import qasync

from networking.client import Client
from .widgets.chat_window import ChatWindow
from .widgets.connect_dialog import ConnectDialog

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

    def handle_connect_request(self, host: str, port: int, alias: str, tls: bool):
        QTimer.singleShot(
            0,
            lambda: asyncio.ensure_future(
                self.connect_to_server(host, port, alias, tls)
            ),
        )

    async def connect_to_server(self, host: str, port: int, alias: str, tls: bool):
        self.client = Client(host, port, alias, tls=tls)
        self.client.set_message_callback(self.on_message_received)

        try:
            await self.client.connect()
            self.connection_status.emit(True)
            self.chat_window.add_message(f"Connected to {host}:{port} as {alias}")
            asyncio.create_task(self.listen_for_messages())
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connection_status.emit(False)
            QMessageBox.critical(self.chat_window, "Connection Error", str(e))
            self.show_connect_dialog()

    def on_message_received(self, message: str):
        self.message_received.emit(message)

    async def send_message(self, message: str):
        if self.client and self.client.writer:
            self.chat_window.add_message(f"You: {message}")
            await self.client.send_message(message)

    def disconnect(self, show_dialog=True):
        if self.client and self.client.writer:
            self.client.writer.close()
            self.client = None
            self.connection_status.emit(False)
            self.chat_window.add_message("Disconnected from server")
            if show_dialog:
                self.show_connect_dialog()

    def handle_window_close(self):
        if self.client and self.client.writer:
            self.client.writer.close()
        QApplication.quit()

    async def listen_for_messages(self):
        try:
            while self.client and self.client.reader:
                await self.client.receive_message()
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            self.connection_status.emit(False)
            self.chat_window.add_message("Connection lost")


def main():
    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    chat_app = ChatApplication()

    def cleanup():
        if chat_app.client and chat_app.client.writer:
            chat_app.client.writer.close()

    app.aboutToQuit.connect(cleanup)

    try:
        with loop:
            loop.run_forever()
    finally:
        cleanup()


if __name__ == "__main__":
    main()
