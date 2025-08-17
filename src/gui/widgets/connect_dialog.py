from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFormLayout,
    QCheckBox,
)
from PyQt5.QtCore import pyqtSignal


class ConnectDialog(QDialog):
    connect_requested = pyqtSignal(str, int, str, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Connect to Server")
        self.setModal(True)
        self.resize(350, 200)

        # Dark theme styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 2px solid #555555;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
                color: #ffffff;
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
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.host_input = QLineEdit("127.0.0.1")
        form_layout.addRow("Host:", self.host_input)

        self.port_input = QLineEdit("50000")
        form_layout.addRow("Port:", self.port_input)

        self.alias_input = QLineEdit("Anonymous")
        form_layout.addRow("Alias:", self.alias_input)

        self.tls_checkbox = QCheckBox("Use TLS")
        form_layout.addRow(self.tls_checkbox)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect)
        button_layout.addWidget(self.connect_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet(
            "QPushButton { background-color: #6c757d; } QPushButton:hover { background-color: #5a6268; } QPushButton:pressed { background-color: #545b62; }"
        )
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def connect(self):
        try:
            host = self.host_input.text().strip()
            port = int(self.port_input.text().strip())
            alias = self.alias_input.text().strip() or "Anonymous"
            tls = self.tls_checkbox.isChecked()

            self.connect_requested.emit(host, port, alias, tls)
            self.accept()
        except ValueError:
            pass
