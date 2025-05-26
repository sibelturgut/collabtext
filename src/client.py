# client.py
# Client-side code for the collaborative text editor
# Clients can own a local file but operate under server permissions
# UI has a text box, Edit button (lock_request), and Done button (release_lock)
# All text box changes are sent and received in real-time across all clients

import socket
import threading
import json
import text_editor
import ui

class Client:
    def __init__(self, server_ip, port, local_file_path=None):
        self.server_ip = server_ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.text_editor = text_editor.TextEditor(local_file_path)
        self.is_editor = False
        self.running = False
        self.ui = ui.App(self)
        self.content_lock = threading.Lock()

    def start(self):
        try:
            self.sock.connect((self.server_ip, self.port))
            self.running = True
            self.request_initial_content()
            threading.Thread(target=self.listen_to_server, daemon=True).start()
            self.ui.run()
        except Exception as e:
            ui.show_error(f"Could not connect to server: {e}") #UI has error pop ups.
            self.running = False 

    def request_initial_content(self):
        try:
            self._send({"type": "REQUEST_CONTENT"})
        except Exception as e:
            ui.show_error(f"Failed to request initial content: {e}")

    def listen_to_server(self):
        while self.running:
            try:
                data = self.sock.recv(8192).decode("utf-8")
                if not data:
                    ui.show_info("Server disconnected.")
                    self.running = False
                    break

                try:
                    message = json.loads(data)
                    self._handle_message(message)
                except json.JSONDecodeError:
                    ui.show_error("Received malformed message from server.")

            except Exception as e:
                ui.show_error(f"Connection lost: {e}")
                self.running = False
                break

    def _handle_message(self, message):
        msg_type = message.get("type")

        if msg_type == "LOCK_GRANTED":
            self.is_editor = True
            self.ui.set_editing_mode(True)

        elif msg_type == "LOCK_DENIED":
            self.is_editor = False
            self.ui.set_editing_mode(False)
            ui.show_info("Lock denied. Another user is editing.")

        elif msg_type == "LOCK_RELEASED":
            self.is_editor = False
            self.ui.set_editing_mode(False)

        elif msg_type == "CONTENT_UPDATE":
            content = message.get("content", "")
            with self.content_lock:
                self.text_editor.content = content
                ui.display_change(content)

        elif msg_type == "INITIAL_CONTENT":
            content = message.get("content", "")
            with self.content_lock:
                self.text_editor.content = content
                ui.display_change(content)

        else:
            ui.show_info(f"[SERVER]: {message}")

    def lock_request(self):
        if not self.running:
            ui.show_error("Not connected to server.")
            return
        try:
            self._send({"type": "LOCK_REQUEST"})
        except Exception as e:
            ui.show_error(f"Failed to request lock: {e}")

    def release_lock(self):
        if not self.running:
            ui.show_error("Not connected to server.")
            return
        if self.is_editor:
            try:
                self._send({"type": "LOCK_RELEASE"})
                self.is_editor = False
                self.ui.set_editing_mode(False)
            except Exception as e:
                ui.show_error(f"Failed to release lock: {e}")

    def send_content_change(self, new_content):
        if not self.running:
            ui.show_error("Not connected to server.")
            return
        if not self.is_editor:
            ui.show_error("Cannot edit: Lock not acquired.")
            return
        try:
            with self.content_lock:
                self.text_editor.content = new_content
                self._send({"type": "CONTENT_UPDATE", "content": new_content})
                ui.display_change(new_content)
        except Exception as e:
            ui.show_error(f"Failed to send content change: {e}")

    def save_local(self):
        try:
            self.text_editor.save_file_content()
            ui.show_info("Content saved locally.")
        except Exception as e:
            ui.show_error(f"Failed to save local content: {e}")

    def disconnect(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
                ui.show_info("Disconnected from server.")
            except Exception as e:
                ui.show_error(f"Error closing connection: {e}")

    def _send(self, message_dict):
        """Send JSON-encoded messages to the server."""
        self.sock.sendall(json.dumps(message_dict).encode("utf-8"))
