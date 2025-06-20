import socket
import threading
import sys
import time

# Banner
BANNER = """
============================================================
          MITM Proxy Master
          Coded by Pakistani Ethical Hacker: Mr Sabaz Ali Khan
============================================================
"""

def log_message(message):
    """Log messages with timestamp."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def handle_client(client_socket, remote_host, remote_port):
    """Handle the client connection and forward to remote server."""
    # Connect to the remote server
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_socket.connect((remote_host, remote_port))
        log_message(f"Connected to remote server {remote_host}:{remote_port}")
    except Exception as e:
        log_message(f"Error connecting to remote server: {e}")
        client_socket.close()
        return

    # Receive data from client
    client_data = b""
    try:
        client_socket.settimeout(2.0)
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            client_data += data
    except socket.timeout:
        pass
    except Exception as e:
        log_message(f"Error receiving client data: {e}")

    if client_data:
        log_message(f"Client Request:\n{client_data.decode('utf-8', errors='ignore')}")
        # Forward client data to remote server
        try:
            remote_socket.sendall(client_data)
        except Exception as e:
            log_message(f"Error forwarding data to server: {e}")

    # Receive response from remote server
    server_data = b""
    try:
        remote_socket.settimeout(2.0)
        while True:
            data = remote_socket.recv(4096)
            if not data:
                break
            server_data += data
    except socket.timeout:
        pass
    except Exception as e:
        log_message(f"Error receiving server data: {e}")

    if server_data:
        log_message(f"Server Response:\n{server_data.decode('utf-8', errors='ignore')}")
        # Forward server response to client
        try:
            client_socket.sendall(server_data)
        except Exception as e:
            log_message(f"Error forwarding data to client: {e}")

    # Close sockets
    remote_socket.close()
    client_socket.close()

def start_proxy(local_host='127.0.0.1', local_port=8080, remote_host='example.com', remote_port=80):
    """Start the MITM proxy server."""
    print(BANNER)
    log_message(f"Starting MITM Proxy on {local_host}:{local_port} forwarding to {remote_host}:{remote_port}")

    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((local_host, local_port))
        server_socket.listen(5)
        log_message("Proxy server started successfully.")
    except Exception as e:
        log_message(f"Error starting proxy server: {e}")
        sys.exit(1)

    while True:
        try:
            client_socket, addr = server_socket.accept()
            log_message(f"New connection from {addr[0]}:{addr[1]}")
            # Handle each client in a separate thread
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, remote_host, remote_port)
            )
            client_thread.start()
        except KeyboardInterrupt:
            log_message("Shutting down proxy server...")
            server_socket.close()
            break
        except Exception as e:
            log_message(f"Error accepting connection: {e}")

if __name__ == "__main__":
    # Configuration
    LOCAL_HOST = "127.0.0.1"
    LOCAL_PORT = 8080
    REMOTE_HOST = "example.com"  # Change to the target server
    REMOTE_PORT = 80  # Change to the target server's port

    start_proxy(LOCAL_HOST, LOCAL_PORT, REMOTE_HOST, REMOTE_PORT)