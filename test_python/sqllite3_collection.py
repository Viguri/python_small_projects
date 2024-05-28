import os
import mutagen
import sqlite3
from tkinter import filedialog, Tk

# Function to extract Genre ID3 tag from audio files
import os

def extract_genre(file_path):
    if not os.path.isfile(file_path) or not os.access(file_path, os.R_OK):
        print(f"File {file_path} is not accessible.")
        return None

    try:
        audio = mutagen.File(file_path)
        if audio:
            if 'TCON' in audio:
                return audio['TCON'].text[0]
            else:
                return None
        else:
            return None
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Function to recursively search for audio files in a directory
def find_audio_files(directory):
    audio_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(('.mp3', '.wav', '.flac')):
                audio_files.append(os.path.join(root, file))
    return audio_files

# Function to create and populate the HyperSQL database
def create_database(audio_files):
    conn = sqlite3.connect('audio_genres.db')
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS AudioFiles
                 (FilePath TEXT PRIMARY KEY, Genre TEXT)''')

    # Insert data into the table
    for file in audio_files:
        genre = extract_genre(file)
        if genre:
            c.execute("INSERT INTO AudioFiles (FilePath, Genre) VALUES (?, ?)", (file, genre))

    conn.commit()
    conn.close()

# Function to get the folder where the audio files are located using Tkinter dialog
def get_folder():
    root = Tk()
    root.withdraw()  # Hide the main window

    folder_path = filedialog.askdirectory(title="Select Folder Containing Audio Files")
    root.destroy()

    return folder_path

# Main function
""" def main():
    # Get the folder where the audio files are located
    directory = get_folder()
    if not directory:
        print("No folder selected. Exiting.")
        return

    # Find audio files in the directory
    audio_files = find_audio_files(directory)

    # Create and populate the database
    create_database(audio_files)

    print("Database created successfully.") """

# Function to fetch data from the database
def fetch_data():
    conn = sqlite3.connect('audio_genres.db')
    c = conn.cursor()
    c.execute("SELECT DISTINCT Genre FROM AudioFiles ORDER BY Genre ASC")
    data = c.fetchall()
    conn.close()
    return data

def main():
    # Fetch data from the database
    data = fetch_data()

    # Print the fetched data
    with open('genres.txt', 'w', encoding='utf-8') as f:
        for row in data:
            print('Filename', row, file=f)

if __name__ == "__main__":
    main()
