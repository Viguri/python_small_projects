import os
import tkinter as tk
from tkinter import filedialog
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import re

def get_genre(file_path):
    try:
        audio = MP3(file_path, ID3=ID3)
        tags = audio.tags
        if 'TCON' in tags:
            genre = tags['TCON'].text[0]
            return genre
        else:
            return None
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def clean_folder_name(name):
    # Remove special characters from folder name
    cleaned_name = re.sub(r'[^\w\s-]', '', name)
    # Remove '\r' characters
    cleaned_name = cleaned_name.replace('\r', '')
    return cleaned_name

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    folder_path = filedialog.askdirectory(title="Select Folder Containing MP3 Files")

    if not folder_path:
        print("No folder selected. Exiting...")
        return

    genres = set()

    # Iterate through files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".mp3"):
            file_path = os.path.join(folder_path, file_name)
            genre = get_genre(file_path)
            if genre:
                genres.add(genre)

    # Create subfolder "genres" if it doesn't exist
    genres_folder = os.path.join(folder_path, "genres")
    if not os.path.exists(genres_folder):
        os.makedirs(genres_folder)

    # Create a folder for each unique genre
    for genre in genres:
        genre_folder_name = clean_folder_name(genre)
        genre_folder_path = os.path.join(genres_folder, genre_folder_name)
        if not os.path.exists(genre_folder_path):
            os.makedirs(genre_folder_path)
            print(f"Created folder for genre '{genre}'")

if __name__ == "__main__":
    main()
