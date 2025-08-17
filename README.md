# NetComm: A Python Chat System

NetComm is a TCP-based chat system built with Python's `asyncio` library. It offers both a command-line interface (CLI) and a graphical user interface (GUI), designed with a modular architecture that separates the networking logic from the user interface. Some features include:

- **Asynchronous:** Built with `asyncio` for high performance and scalability.
- **CLI and GUI:** Choose between a simple command-line client or a user-friendly GUI.
- **Secure:** Supports TLS encryption for secure communication.
- **Modular Design:** Core networking, CLI, and GUI components are separated for maintainability.

## Getting Started

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/virusmint/NetComm.git
   cd NetComm
   ```

2. Install the project with the desired extras (e.g., `gui`, `cli`):

   ```bash
   pip install .[gui,cli]
   ```

### Usage

#### Server

To start the chat server, run the following command:

```bash
netcomm-server [options]
```

**Options:**

- `--host`: The host address to bind the server to (default: `0.0.0.0`).
- `--port`: The port to bind the server to (default: `50000`).
- `--tls`: Enable TLS encryption.

#### Client CLI

To use the CLI client, run:

```bash
netcomm-cli [options]
```

**Options:**

- `--host`: The server host address (default: `127.0.0.1`).
- `--port`: The server port (default: `50000`).
- `--alias`: Your alias in the chat (default: `Anonymous`).
- `--tls`: Enable TLS encryption.

#### Client GUI

To launch the GUI client, run:

```bash
netcomm-gui
```

The GUI will open a dialog to enter the server host, port, and alias. You can also enable TLS encryption by checking the "Use TLS" box.

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
