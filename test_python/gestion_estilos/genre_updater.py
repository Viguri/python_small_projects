import os
import eyed3
import json
from tkinter import Tk, filedialog
from collections import defaultdict
from datetime import datetime

# Generate a timestamp string
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# File to store the genre mapping with a timestamp
GENRE_MAPPING_FILE = f"genre_mapping_{timestamp}.json"

# Function to load the genre mapping from a JSON file
def load_genre_mapping(file_path=GENRE_MAPPING_FILE):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # Return an empty mapping if the file doesn't exist
        return {}

# Function to save the genre mapping to a JSON file
def save_genre_mapping(genre_mapping, file_path=GENRE_MAPPING_FILE):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(genre_mapping, f, ensure_ascii=False, indent=4)

# Function to read genre from ID3 tags
def read_id3_genre(file_path):
    try:
        audio = eyed3.load(file_path)
        if audio and audio.tag and audio.tag.genre:
            return audio.tag.genre.name
    except Exception as e:
        print(f"Error reading genre from {file_path}: {e}")
    return None

# Function to scan files in a directory and collect new genres
def scan_files_for_genres(directory):
    new_genres = defaultdict(set)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith('.mp3'):
                file_path = os.path.join(root, file)
                genre = read_id3_genre(file_path)
                if genre:
                    new_genres[genre].add(file_path)
    return new_genres

# Function to update the genre mapping with new genres
def update_genre_mapping(genre_mapping, new_genres):
    for genre, files in new_genres.items():
        if genre not in genre_mapping:
            genre_mapping[genre] = []
        genre_mapping[genre].extend(files)
    return genre_mapping

# Main function to run the genre updater
def main():
    # Hide the root window of Tkinter
    Tk().withdraw()

    # Ask the user to select a directory
    directory = filedialog.askdirectory(title="Select Directory to Scan for MP3 Files")

    if directory:
        # Load the existing genre mapping
        genre_mapping = load_genre_mapping()

        # Scan the selected directory for new genres
        new_genres = scan_files_for_genres(directory)

        # Update the genre mapping with new genres
        updated_genre_mapping = update_genre_mapping(genre_mapping, new_genres)

        # Save the updated genre mapping to the JSON file
        save_genre_mapping(updated_genre_mapping)

        print(f"Genre mapping updated and saved to {GENRE_MAPPING_FILE}")
    else:
        print("No directory selected. Exiting.")

if __name__ == "__main__":
    main()