# Network Communication Chat System

A simple asynchronous TCP-based chat system implemented in Python using asyncio. The system consists of a server that can handle multiple concurrent clients and relay messages between them.

## Components

### Server (`server.py`)

- Asynchronous TCP server that listens on configurable host/port (default: 127.0.0.1:50000)
- Handles multiple concurrent client connections
- Implements message broadcasting with split-horizon (messages aren't echoed back to sender)
- Client alias support through initial handshake protocol
- Comprehensive logging for connection events and errors

### Client (`client.py`)

- Asynchronous TCP client with command-line argument support
- Concurrent sending and receiving of messages
- Configurable server connection (default: 127.0.0.1:50000)
- User alias/nickname support
- Graceful exit with "exit" or "quit" commands

## Usage

### Starting the Server

```bash
python server.py --host <server_ip> --port <server_port>
```

### Connecting with Client

```bash
python client.py --host <server_ip> --port <server_port> --name <your_alias>
```

Example:

```bash
python client.py --host 127.0.0.1 --port 50000 --name "Alice"
```

## TODO / Potential Improvements

### Security & Robustness

- [ ] Add input validation and sanitization for messages and aliases
- [ ] Implement authentication/authorization system
- [ ] Add rate limiting to prevent message flooding
- [ ] Implement proper SSL/TLS encryption for secure communication
- [ ] Add message size limits to prevent buffer overflow attacks

### Error Handling & Reliability

- [ ] Improve graceful handling of client disconnections
- [ ] Add connection timeout handling
- [ ] Implement automatic reconnection logic in client
- [ ] Add server shutdown signal handling (SIGTERM, SIGINT)
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
