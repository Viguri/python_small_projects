import tkinter as tk
from tkinter import filedialog
import os
import csv
import shutil
import mutagen
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from tqdm import tqdm
import time

def move_files():
    start_time = time.time()  # Start time tracking

    files_location = filedialog.askdirectory(title="Select Folder with MP3/FLAC Files")
    if not files_location:
        print("No folder selected. Aborting.")
        return

    matches_file = filedialog.askopenfilename(title="Select CSV File with Genre Matches", filetypes=[("CSV Files", "*.csv")])
    if not matches_file:
        print("No CSV file selected. Aborting.")
        return

    genre_mapping = {}

    with open(matches_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            genre_mapping[row['Genre'].strip()] = (row['styleName'].strip(), row['folderName'].strip())

    print("Genre Mapping:")
    for genre, (style_name, folder_name) in genre_mapping.items():
        print(f"Genre: {genre}, Style Name: {style_name}, Folder Name: {folder_name}")

    new_structure_folder = os.path.join(files_location, "NEW_STRUCTURE_05052024")
    if not os.path.exists(new_structure_folder):
        os.makedirs(new_structure_folder)

    print(f"New Structure Folder: {new_structure_folder}")

    no_genre_folder = os.path.join(new_structure_folder, "NO_GENRE")
    if not os.path.exists(no_genre_folder):
        os.makedirs(no_genre_folder)

    print(f"No Genre Folder: {no_genre_folder}")

    total_files = sum(len(files) for _, _, files in os.walk(files_location))
    progress_bar = tqdm(total=total_files, desc="Processing Files", unit="file")

    files_found = 0
    files_skipped = 0
    files_not_identified = 0

    for root, _, files in os.walk(files_location):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac')):
                file_path = os.path.join(root, file)
                try:
                    genre = get_genre(file_path)
                    if genre and genre in genre_mapping:
                        files_found += 1
                    else:
                        files_not_identified += 1
                except mutagen.mp3.HeaderNotFoundError:
                    files_skipped += 1
                    continue
                progress_bar.update(1)

    progress_bar.close()

    progress_bar = tqdm(total=total_files, desc="Copying Files", unit="file")
    for root, _, files in os.walk(files_location):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac')):
                file_path = os.path.join(root, file)
                try:
                    genre = get_genre(file_path)
                    if genre and genre in genre_mapping:
                        style_name, folder_name = genre_mapping[genre]
                        destination_folder = os.path.join(new_structure_folder, style_name, folder_name)
                        if not os.path.exists(destination_folder):
                            os.makedirs(destination_folder)
                        destination_path = os.path.join(destination_folder, file).replace("\\", "/")
                        if destination_folder != new_structure_folder and not os.path.exists(destination_path):
                            try:
                                print(f"Copying {file} to {destination_path}")
                                shutil.copy2(file_path, destination_path)
                            except PermissionError:
                                files_skipped += 1
                    else:
                        destination_folder = no_genre_folder
                        if not os.path.exists(destination_folder):
                            os.makedirs(destination_folder)
                        destination_path = os.path.join(destination_folder, file).replace("\\", "/")
                        if destination_folder != new_structure_folder and not os.path.exists(destination_path):
                            try:
                                print(f"Copying {file} to {destination_path}")
                                shutil.copy2(file_path, destination_path)
                                files_not_identified += 1
                            except PermissionError:
                                files_skipped += 1
                except mutagen.mp3.HeaderNotFoundError:
                    files_skipped += 1
                    continue
                progress_bar.update(1)
    progress_bar.close()

    elapsed_time = time.time() - start_time  # Calculate elapsed time

    statistics_message = f"Total files: {total_files}\nFiles found based on Genre: {files_found}\nFiles skipped: {files_skipped}\nFiles not identified: {files_not_identified}\nElapsed Time: {elapsed_time:.2f} seconds"
    with open("results.txt", "w") as f:
        f.write(statistics_message)

def get_genre(file_path):
    if file_path.lower().endswith('.mp3'):
        audio = MP3(file_path)
        genre = audio.get('TCON')
        return genre[0] if genre else None
    elif file_path.lower().endswith('.flac'):
        flac_tags = FLAC(file_path)
        genre = flac_tags.get('genre')
        return genre[0] if genre else None
    return None

# Create GUI
root = tk.Tk()
root.withdraw()  # Hide the main window

move_files()  # Call the function to initiate the file moving process
