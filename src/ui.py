import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from tkinter import filedialog
from text_editor import TextEditor


class TextEditorUI:
    def __init__(self, root, editor: TextEditor, is_server=False):
        self.root = root
        self.editor = editor
        self.is_server = is_server
        self.locked = False

        self.root.title("Collaborative Text Editor")

        # Create a frame to hold the text widget with padding
        self.frame = ttk.Frame(self.root, padding=10)
        self.frame.pack(fill=BOTH, expand=YES)

        # Text area with scrollbars
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

        # Server or client menu
        if self.is_server:
            self.menu.add_command(label="Broadcast Change", command=self.broadcast_change)
            self.menu.add_command(label="Release Lock", command=self.release_lock)
        else:
            self.menu.add_command(label="Request Lock", command=self.lock_request)

        self.text_area.insert("1.0", self.editor.content)
        self.text_area.bind("<<Modified>>", self.on_text_change)

    def open_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.editor.file_path = file_path
            self.editor.retrieve_file_content()
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", self.editor.content)

    def save_file(self):
        self.editor.content = self.text_area.get("1.0", "end")
        self.editor.save_file_content()

    def on_text_change(self, event=None):
        if not self.locked:
            self.editor.content = self.text_area.get("1.0", "end")
            if self.is_server:
                self.broadcast_change()
        else:
            Messagebox.show_info("Document is locked. Cannot edit.", title="Lock Active")
            self.text_area.delete("1.0", "end")
            self.text_area.insert("1.0", self.editor.content)
        self.text_area.edit_modified(False)

    def broadcast_change(self):
        # Placeholder: Integrate with server.py
        print("[DEBUG] Broadcasting change to all clients...")

    def display_change(self, new_content):
        self.text_area.delete("1.0", "end")
        self.text_area.insert("1.0", new_content)
        self.editor.content = new_content

    def lock_request(self):
        # Placeholder: Send lock request to server
        print("[DEBUG] Lock request sent to server...")

    def release_lock(self):
        self.locked = False
        print("[DEBUG] Lock released.")


def App(is_server=False, theme="flatly"):
    app = ttk.Window(title="Collaborative Text Editor", themename=theme, size=(800, 600))
    editor = TextEditor()
    TextEditorUI(app, editor, is_server=is_server)
    app.mainloop()


if __name__ == "__main__":
    App(is_server=False, theme="solar")
  # Set True if testing as server
