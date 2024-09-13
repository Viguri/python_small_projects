import os
import shutil
import tkinter as tk
from tkinter import filedialog
from mutagen.id3 import ID3NoHeaderError, ID3
from mutagen.mp3 import MP3
from mutagen.mp3 import HeaderNotFoundError
import os
import shutil
import hashlib

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



def calculate_hash(file_path, block_size=65536):
    """
    Calculate SHA256 hash of a file
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def find_duplicates_in_folder(folder_path):
    """
    Find duplicate files in a folder based on size and SHA256 hash
    """
    duplicates = {}
    for root, _, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            size = os.path.getsize(file_path)
            file_hash = calculate_hash(file_path)
            if (size, file_hash) in duplicates:
                duplicates[(size, file_hash)].append(file_path)
            else:
                duplicates[(size, file_hash)] = [file_path]
    return {k: v for k, v in duplicates.items() if len(v) > 1}

def move_duplicates_to_folder(duplicates, folder_path):
    """
    Move duplicate files to a subfolder named 'duplicates'
    """
    duplicates_folder_path = os.path.join(folder_path, 'duplicates')
    if not os.path.exists(duplicates_folder_path):
        os.makedirs(duplicates_folder_path)

    for duplicate_files in duplicates.values():
        for i, file_path in enumerate(duplicate_files[1:], start=1):
            new_file_path = os.path.join(duplicates_folder_path, f"{i}_{os.path.basename(file_path)}")
            try:
                shutil.move(file_path, new_file_path)
            except Exception as e:
                print(f"Error moving file {file_path} to {new_file_path}: {e}")

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
        for key, duplicate_files in duplicates.items():
            print(f"Size: {key[0]}, Hash: {key[1]}")
            for file_path in duplicate_files:
                print(f"\t{file_path}")
    move_duplicates_to_folder(duplicates, folder_path)
    print("Duplicate files moved to 'duplicates' folder.")

if __name__ == "__main__":
    main()
