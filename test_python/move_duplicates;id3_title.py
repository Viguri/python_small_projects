import os
import shutil
import tkinter as tk
from tkinter import filedialog
from mutagen.id3 import ID3NoHeaderError, ID3

def get_title_from_id3(file_path):
    """
    Get Title from ID3 tag
    """
    try:
        audiofile = ID3(file_path)
        title = audiofile.get('TIT2').text[0] if 'TIT2' in audiofile else None
        return title
    except (ID3NoHeaderError, KeyError) as e:
        print(f"Error processing file {file_path}: {e}")
        return None

def find_duplicates_in_folder(folder_path):
    """
    Find duplicate files in a folder based on ID3 tag (Title), size, and duration
    """
    duplicates = {}
    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            title = get_title_from_id3(file_path)
            if title:
                size = os.path.getsize(file_path)
                duration = os.path.getctime(file_path)  # Just using file creation time as a placeholder for duration
                if (title, size, duration) in duplicates:
                    duplicates[(title, size, duration)].append(file_path)
                else:
                    duplicates[(title, size, duration)] = [file_path]
    return {k: v for k, v in duplicates.items() if len(v) > 1}

def move_duplicates_to_folder(duplicates, folder_path):
    """
    Move duplicate files to a folder named 'duplicates'
    """
    duplicates_folder = os.path.join(folder_path, "duplicates")
    os.makedirs(duplicates_folder, exist_ok=True)
    for duplicate_files in duplicates.values():
        for file_path in duplicate_files[1:]:
            shutil.move(file_path, duplicates_folder)

def main():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Folder")
    if not folder_path:
        print("No folder selected. Exiting.")
        return

    duplicates = find_duplicates_in_folder(folder_path)
    if not duplicates:
        print("No duplicates found.")
        return

    print("Found Duplicates:")
    for key, value in duplicates.items():
        print(f"Title: {key[0]}, Size: {key[1]}, Duration: {key[2]}")
        for file_path in value:
            print(f"- {file_path}")

    move_duplicates_to_folder(duplicates, folder_path)
    print("Duplicate files moved to 'duplicates' folder.")

if __name__ == "__main__":
    main()
