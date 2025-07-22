from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont


class ChatWindow(QWidget):
    message_sent = pyqtSignal(str)
    disconnect_requested = pyqtSignal()
    window_closing = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Chat Client")
        self.setGeometry(100, 100, 800, 600)

        # Dark theme styling
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                line-height: 1.4;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                border-radius: 5px;
                color: white;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
            #disconnect_button {
                background-color: #dc3545;
                border: 1px solid #dc3545;
                color: white;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            #disconnect_button:hover {
                background-color: #c82333;
                border-color: #bd2130;
            }
        """)

        layout = QVBoxLayout()

        # Status bar with disconnect button
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("Disconnected")
        self.status_label.setStyleSheet(
            "color: #ff6b6b; font-weight: bold; background-color: #3c3c3c; border-radius: 5px; padding: 8px;"
        )
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.disconnect_button = QPushButton("↵ Disconnect")
        self.disconnect_button.setObjectName("disconnect_button")
        self.disconnect_button.setToolTip("Disconnect and return to connect dialog")
        self.disconnect_button.clicked.connect(self.disconnect_requested.emit)
        self.disconnect_button.setEnabled(False)
        status_layout.addWidget(self.disconnect_button)
        
        layout.addLayout(status_layout)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Consolas", 11))
        # Ensure HTML formatting is enabled for proper text alignment
        self.chat_display.setHtml("")
        layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setStyleSheet(
            self.message_input.styleSheet()
            + "QLineEdit { color: #ffffff; } QLineEdit::placeholder { color: #888888; }"
        )
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        layout.addLayout(input_layout)

        self.setLayout(layout)

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            self.message_sent.emit(message)
            self.message_input.clear()

    def add_message(self, message: str):
        if self.is_system_message(message):
            # System messages with special color and bold, but left-aligned
            self.chat_display.append(f'<p style="color: #87ceeb; font-weight: bold; padding: 10px; margin: 15px 0;">{message}</p>')
        else:
            # User messages use default styling
            self.chat_display.append(message)
    
    def is_system_message(self, message: str):
        system_keywords = [
            "Connected to",
            "Disconnected from server",
            "joined the chat",
            "left the chat",
            "has disconnected"
        ]
        return any(keyword in message for keyword in system_keywords)

    def set_connected(self, connected: bool):
        if connected:
            self.status_label.setText("🟢 Connected")
            self.status_label.setStyleSheet(
                "color: #51cf66; font-weight: bold; background-color: #3c3c3c; border-radius: 5px; padding: 8px;"
            )
            self.message_input.setEnabled(True)
            self.send_button.setEnabled(True)
            self.disconnect_button.setEnabled(True)
        else:
            self.status_label.setText("🔴 Disconnected")
            self.status_label.setStyleSheet(
                "color: #ff6b6b; font-weight: bold; background-color: #3c3c3c; border-radius: 5px; padding: 8px;"
            )
            self.message_input.setEnabled(False)
            self.send_button.setEnabled(False)
            self.disconnect_button.setEnabled(False)

    def closeEvent(self, event):
        # Signal window is closing to handle cleanup without showing dialog
        self.window_closing.emit()
        event.accept()

