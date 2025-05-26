#this class represents the server side.
#in our application server is also a user, but the one who host the file
#server initiates and waits for new connections
#server user has the chance to select port and maybe other configurations if necessary 
#maybe we can add a security configuration (select ip addresses who can connect)

import threading
import socket
from text_editor import TextEditor

class Server:
    def __init__(self, host='0.0.0.0', port=12345, max_connections=5, allowed_ips=None, file_path="your_file.txt"):
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.allowed_ips = allowed_ips  # List of allowed IPs, or None for open access
        self.active_connections = 0
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.text_editor = TextEditor(file_path=file_path)  # or pass as argument
        self.clients = []
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(self.max_connections)
        print(f"Server started on {self.host}:{self.port}. Waiting for connections...")

        while self.active_connections < self.max_connections: # hwo many connections we want to allow
            #race cond? here
            self.active_connections += 1 # just counter, ! this counter should be decremented or take care of this after the sufficient connection
            client_socket, addr = self.server_socket.accept() # accepts a new connection, to get IP,port and object
            print(f"Connection from {addr}") # It will be decided if the connection is allowed or not
            # generate a new thread for each connection here, call connect() function?, with addr and client_socket as arguments
            #connect()

    def connect(self, client_socket, addr): #function to use in threads. threads will call this function for each connection and keep connected
        if self.allowed_ips is not None and addr[0] not in self.allowed_ips:#0 is IP, 1 is port
            print(f"Connection from {addr[0]} rejected. Not in allowed IPs.")
            client_socket.close() # rejected client connection
            return
        self.clients.append(client_socket) # add client to the list of connected clients, disconnect should remove them and also decrease the counter
        # we can send a notification to the client that they are connected here
        client_socket.sendall(b"Welcome to the server!\n") # or uncomment
        print(f"Client {addr[0]} connected.")

    def broadcast_changes(self):
        message = self.text_editor.content  # or retrieve_file_content() if needed ?
        for client in self.clients:
            try:
                client.sendall(message.encode()) # client .decode() needed, byte to string
            except Exception as e:
                print(f"Error sending to client: {e}")
                self.clients.remove(client)
                client.close()

    def acquire_lock():
        pass

    def release_lock():
        pass