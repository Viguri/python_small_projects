import tkinter as tk
from tkinter import filedialog
import os
import csv
import shutil
from mutagen.flac import FLAC
import eyed3

def move_files():
    files_location = filedialog.askdirectory(title="Select Folder with MP3/FLAC Files")
    if not files_location:
        return

    matches_file = filedialog.askopenfilename(title="Select CSV File with Genre Matches", filetypes=[("CSV Files", "*.csv")])
    if not matches_file:
        return

    # Dictionary to store mapping of genre to style name and folder name
    genre_mapping = {}

    # Read the CSV file and populate the genre mapping dictionary
    with open(matches_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            genre_mapping[row['Genre'].strip()] = (row['styleName'].strip(), row['folderName'].strip())

    # Create 'NEW_STRUCTURE' folder if it doesn't exist
    new_structure_folder = os.path.join(files_location, "NEW_STRUCTURE")
    if not os.path.exists(new_structure_folder):
        os.makedirs(new_structure_folder)

    # Initialize counters
    total_files = 0
    files_found = 0
    files_skipped = 0
    files_not_identified = 0

    # Create folders based on genre and subfolders based on folderName
    for root, _, files in os.walk(files_location):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac')):
                total_files += 1
                file_path = os.path.join(root, file)
                genre = get_genre(file_path)
                if genre and genre in genre_mapping:
                    files_found += 1
                    style_name, folder_name = genre_mapping[genre]
                    style_folder = os.path.join(new_structure_folder, style_name)
                    if not os.path.exists(style_folder):
                        os.makedirs(style_folder)
                    folder_path = os.path.join(style_folder, folder_name)
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                else:
                    files_not_identified += 1

    # Ask for confirmation before copying files
    confirm = tk.messagebox.askyesno(title="Confirmation", message="Folders created successfully. Do you want to continue and copy files?")
    if not confirm:
        return

    # Copy files to corresponding folders, skipping files in use by another process
    for root, _, files in os.walk(files_location):
        for file in files:
            if file.lower().endswith(('.mp3', '.flac')):
                file_path = os.path.join(root, file)
                genre = get_genre(file_path)
                if genre and genre in genre_mapping:
                    style_name, folder_name = genre_mapping[genre]
                    destination_folder = os.path.join(new_structure_folder, style_name, folder_name)
                    try:
                        shutil.copy2(file_path, os.path.join(destination_folder, file))
                    except PermissionError:
                        print(f"Skipping file: {file_path} - File is in use by another process")
                        files_skipped += 1

    # Display statistics
    statistics_message = f"Total files: {total_files}\nFiles found based on Genre: {files_found}\nFiles skipped: {files_skipped}\nFiles not identified: {files_not_identified}"
    tk.messagebox.showinfo(title="Copy Files", message=f"Files copied successfully!\n\n{statistics_message}")

    # Write statistics to file
    with open("results.txt", "w") as f:
        f.write(statistics_message)

def get_genre(file_path):
    if file_path.lower().endswith('.mp3'):
        audiofile = eyed3.load(file_path)
        if audiofile and audiofile.tag and audiofile.tag.genre:
            return audiofile.tag.genre.name
    elif file_path.lower().endswith('.flac'):
        flac_tags = FLAC(file_path)
        if 'genre' in flac_tags:
            return flac_tags['genre'][0]
    return None

# Create GUI
root = tk.Tk()
root.title("Copy MP3/FLAC Files by Genre")

# Create and position the move button
move_button = tk.Button(root, text="Copy Files", command=move_files)
move_button.pack(pady=10)

# Run the GUI
root.mainloop()
