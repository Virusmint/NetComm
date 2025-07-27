# Network Communication Chat System

A comprehensive asynchronous TCP-based chat system implemented in Python using asyncio. The system provides both command-line and GUI interfaces, with a modular architecture separating core networking functionality from user interfaces.


## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## TLS/SSL Setup

The system supports TLS encryption for secure communication. To enable TLS:

### Generate SSL Certificates

Create a self-signed certificate for testing:

```bash
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes
```

For production, use certificates from a trusted Certificate Authority.

### Certificate Files

Place your certificate files in the project directory:
- `server.crt` - SSL certificate
- `server.key` - Private key

## Usage

### Starting the Server

#### Without TLS (default):
```bash
python -m src.networking.server --host <server_ip> --port <server_port>
```

#### With TLS encryption:
```bash
python -m src.networking.server --host <server_ip> --port <server_port> --tls
```

The server will automatically use `server.crt` and `server.key` files when TLS is enabled.

### GUI Client

```bash
python -m src.interfaces.gui.client_gui
```

The GUI will prompt you to connect to a server with host, port, and alias configuration.

### Command Line Client

#### Without TLS:
```bash
python -m src.interfaces.cli.client_cli --host <server_ip> --port <server_port> --name <your_alias>
```

#### With TLS:
```bash
python -m src.interfaces.cli.client_cli --host <server_ip> --port <server_port> --name <your_alias> --tls
```

Example:
```bash
python -m src.interfaces.cli.client_cli --host 127.0.0.1 --port 50000 --name "Alice" --tls
```

## Project Structure

```
network_comm/
├── src/
│   ├── __init__.py
│   ├── interfaces/
│   │   ├── __init__.py
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   └── client_cli.py
│   │   └── gui/
│   │       ├── __init__.py
│   │       ├── client_gui.py
│   │       └── widgets/
│   │           ├── __init__.py
│   │           ├── chat_window.py
│   │           └── connect_dialog.py
│   └── networking/
│       ├── __init__.py
│       ├── client.py
│       ├── server.py
│       └── protocol/
│           ├── __init__.py
│           └── io.py
├── requirements.txt
└── README.md
```

## Dependencies

- **PyQt5**: GUI framework for the graphical interface
- **qasync**: Asyncio integration with Qt event loop

## TODO / Potential Improvements

### Security & Robustness

- [ ] Add input validation and sanitization for messages and aliases
- [ ] Implement authentication/authorization system
- [ ] Add rate limiting to prevent message flooding
- [x] Implement proper SSL/TLS encryption for secure communication
- [ ] Add message size limits to prevent buffer overflow attacks

### Error Handling & Reliability

- [x] Improve graceful handling of client disconnections
- [ ] Add connection timeout handling
- [ ] Implement automatic reconnection logic in client
- [x] Add server shutdown signal handling (SIGTERM, SIGINT)
- [ ] Better error recovery for network interruptions

### Features

- [ ] Add private messaging capabilities
- [ ] Implement chat rooms/channels
- [ ] Add message history/logging
- [ ] Support for file transfers
- [ ] Add user list/who's online functionality
- [ ] Implement message timestamps
- [ ] Add file transfer capabilities
- [x] Announce new users joining/leaving the chat
- [x] GUI interface with PyQt5
- [ ] Message formatting (bold, italic, colors)
- [ ] Emoji support in GUI
- [ ] Sound notifications for new messages

### Configuration & Deployment

- [ ] Add configuration file support (JSON/YAML)
- [ ] Environment variable configuration
- [ ] Docker containerization
- [ ] Add proper packaging with setup.py/pyproject.toml
- [ ] Unit and integration tests

### Code Quality

- [ ] Add type hints throughout the codebase
- [ ] Implement proper exception classes
- [ ] Add docstrings to all methods and classes
- [x] Code linting and formatting (black, flake8, mypy)
- [ ] Performance profiling and optimization

### Protocol Improvements

- [ ] Design proper message protocol with headers
- [ ] Add message acknowledgments
- [ ] Implement keep-alive/heartbeat mechanism
- [ ] Support for different message types (text, system, private)
