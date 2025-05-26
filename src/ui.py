# ui.py
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog


class TextEditorUI:
    def __init__(self, root, client, is_server=False):
        self.root = root
        self.client = client
        self.is_server = is_server
        self.locked = False  # Local locked flag; can sync with client.is_editor if needed

        self.root.title("Collaborative Text Editor")

        # Frame to hold text widget
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill=BOTH, expand=YES)

        # Text widget with scrollbar
        self.text_area = ttk.ScrolledText(self.frame, wrap=WORD, font=("Segoe UI", 11))
        self.text_area.pack(fill=BOTH, expand=YES)

        # Menu bar
        self.menu = ttk.Menu(self.root)
        self.root.config(menu=self.menu)

        # File menu
        file_menu = ttk.Menu(self.menu, tearoff=False)
        self.menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Lock menu depending on server or client mode
        if self.is_server:
            # Removed the broadcast menu command here
            self.menu.add_command(label="Release Lock", command=self.release_lock)
        else:
            self.menu.add_command(label="Request Lock", command=self.lock_request)

        # Initialize content from client's editor content
        self.text_area.insert("1.0", self.client.text_editor.content)
        self.text_area.bind("<<Modified>>", self.on_text_change)

        # Initially set editing mode based on client state
        self.set_editing_mode(self.client.is_editor)

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.client.text_editor.file_path = file_path
            self.client.text_editor.retrieve_file_content()
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", self.client.text_editor.content)

    def save_file(self):
        self.client.text_editor.content = self.text_area.get("1.0", "end-1c")
        try:
            self.client.text_editor.save_file_content()
            Messagebox.show_info("Content saved successfully.")
        except Exception as e:
            Messagebox.show_error(f"Failed to save content: {e}")

    def on_text_change(self, event=None):
        if self.locked or not self.client.is_editor:
            # Not allowed to edit - revert to current content
            Messagebox.show_info("Document is locked. Cannot edit.", title="Lock Active")
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", self.client.text_editor.content)
        else:
            # User editing allowed: send content update if server or client
            new_content = self.text_area.get("1.0", "end-1c")
            self.client.text_editor.content = new_content

            if self.is_server:
                # Automatically broadcast changes to clients on server side
                self.broadcast_change()
            else:
                # Clients send changes through client methods (usually via networking)
                self.client.send_content_change(new_content)

        self.text_area.edit_modified(False)

    def broadcast_change(self):
        # Server side: send current content to all clients
        print("[DEBUG] Broadcasting change to clients...")
        self.client.broadcast_content_to_clients(self.client.text_editor.content)

    def display_change(self, new_content):
        # Update UI text without triggering
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", new_content)
        self.client.text_editor.content = new_content
        # Lock editing if not client.is_editor
        if not self.client.is_editor:
            self.text_area.config(state="disabled")
        else:
            self.text_area.config(state="normal")
        self.text_area.edit_modified(False)

    def lock_request(self):
        # Client sends lock request to server
        self.client.lock_request()

    def release_lock(self):
        # Client releases lock (or server unlocks)
        self.locked = False
        self.client.release_lock()

    def set_editing_mode(self, can_edit: bool):
        # Enable or disable editing based on lock state
        if can_edit:
            self.text_area.config(state="normal")
            self.locked = False
        else:
            self.text_area.config(state="disabled")
            self.locked = True


def App(is_server=False, theme="flatly"):
    app = ttk.Window(title="Collaborative Text Editor", themename=theme, size=(800, 600))
    # The caller should provide the client instance
    from client import Client
    client = Client(server_ip="127.0.0.1", port=12345)  # Example, adjust as needed
    TextEditorUI(app, client, is_server=is_server)
    app.mainloop()


if __name__ == "__main__":
    App(is_server=False, theme="solar")
