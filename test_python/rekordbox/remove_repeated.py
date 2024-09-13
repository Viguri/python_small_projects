import os
import tkinter as tk
from tkinter import filedialog
import eyed3

def remove_files_with_same_title(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.mp3') or filename.endswith('.flac'):
            file_path = os.path.join(directory, filename)
            audiofile = eyed3.load(file_path)
            if audiofile is not None and audiofile.tag is not None:
                if audiofile.tag.title and audiofile.tag.title.lower() == filename.lower():
                    os.remove(file_path)
                    print(f"Removed {filename}")

def select_folder():
    root = tk.Tk()
    root.withdraw() # Hide the main window
    folder_path = filedialog.askdirectory() # Open folder selection dialog
    return folder_path

# Select folder containing music files
directory_path = select_folder()

# Check if folder is selected
if directory_path:
    remove_files_with_same_title(directory_path)
else:
    print("No folder selected.")
