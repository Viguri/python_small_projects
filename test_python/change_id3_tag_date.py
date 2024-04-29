import os
import tkinter as tk
from tkinter import filedialog
import eyed3

def capitalize_filenames(folder_path):
    for filename in os.listdir(folder_path):
        old_file = os.path.join(folder_path, filename)
        new_filename = filename.lstrip()  # Remove leading spaces
        new_file = os.path.join(folder_path, new_filename.capitalize())
        os.rename(old_file, new_file)

def capitalize_id3_tags(folder_path):
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isfile(filepath) and filename.lower().endswith('.mp3'):
            audiofile = eyed3.load(filepath)
            if audiofile.tag:
                # Remove leading spaces from artist and title
                artist = audiofile.tag.artist.strip() if audiofile.tag.artist else None
                title = audiofile.tag.title.strip() if audiofile.tag.title else None
                # Capitalize first character of each word
                audiofile.tag.artist = artist.capitalize() if artist else None
                audiofile.tag.title = title.capitalize() if title else None
                audiofile.tag.save()

def select_folder_dialog():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    folder_path = filedialog.askdirectory(title="Select Folder")
    return folder_path

def main():
    folder_path = select_folder_dialog()
    if folder_path:
        capitalize_filenames(folder_path)
        capitalize_id3_tags(folder_path)
        print("File names and ID3 tags capitalized successfully.")

if __name__ == "__main__":
    main()
