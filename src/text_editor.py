
class TextEditor:

    #add text variable to keep content

    def __init__(self, file_path = None):
        self.file_path = file_path
        self.content = ""
        self.retrieve_file_content()

    def retrieve_file_content(self, file_path= None):
        if self.file_path is not None:
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    self.content = f.read()
                    print("[INFO] File content loaded.")
            except FileNotFoundError:
                print("[WARNING] File not found. Starting with empty content.")
                self.content = ""
        else:
            print("[INFO] No file path provided. Starting with empty content.")
            self.content = ""

    def save_file_content(self):
        #when users stop using the app, save the file content back to original file on pc of server user
        #if a client user wants to save, create a new file and save the content inside
        if self.file_path is None:
            self.file_path = input("No file path provided. Please enter a path to save the file: ")

        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(self.content)
                print(f"[INFO] Content saved to '{self.file_path}'.")
        except Exception as e:
            print(f"[ERROR] Could not save content: {e}")
