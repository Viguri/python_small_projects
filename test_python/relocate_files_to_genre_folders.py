import os
import shutil
from tkinter import Tk, filedialog
import eyed3

def read_id3_tags(file_path):
    try:
        audio = eyed3.load(file_path)
        if audio and audio.tag:
            id3_tags = {}
            genre = audio.tag.genre
            if genre:
                genre_name = genre.name.replace('\r', '')
                id3_tags['genre'] = genre_name
            else:
                id3_tags['genre'] = ""  # Genre tag may not exist or be empty
            return id3_tags
        else:
            return None
    except (eyed3.id3.tag.TagException, eyed3.id3.frames.FrameError) as e:
        print(f"Error reading tags from {file_path}: {e}")
        return None

def sanitize_genre(genre):
    rare_characters = ['/', '&']
    for char in rare_characters:
        genre = genre.replace(char, '')
    return genre

def create_genre_folders(files_dir, id3_tags):
    genres = set()
    for file_name, tags in id3_tags.items():
        if 'genre' in tags:
            genre = sanitize_genre(tags['genre'])
            tags['genre'] = genre
            if genre:
                genre = ' '.join(genre.split())  # Remove consecutive spaces
                genres.add(genre)

    for genre in genres:
        genre_folder = os.path.join(files_dir, genre)
        os.makedirs(genre_folder, exist_ok=True)

    return genres

def move_files_to_genre_folders(files_dir, id3_tags, genres):
    error_folder = os.path.join(files_dir, "_WithErrors")
    os.makedirs(error_folder, exist_ok=True)

    files_moved = 0
    error_files = 0
    genre_files = {genre: 0 for genre in genres}

    for file_name, tags in id3_tags.items():
        if 'genre' in tags:
            genre = tags['genre']
            if genre in genres:
                shutil.move(os.path.join(files_dir, file_name), os.path.join(files_dir, genre, file_name))
                genre_files[genre] += 1
                files_moved += 1
            else:
                shutil.move(os.path.join(files_dir, file_name), os.path.join(error_folder, file_name))
                error_files += 1
                print(f"Error moving file {file_name} to corresponding folder: Genre '{genre}' not found in detected genres.")

    return files_moved, error_files, genre_files

def main():
    root = Tk()
    root.withdraw()  # Hide the main window

    files_dir = filedialog.askdirectory(title="Select Folder Containing MP3 Files")

    if not files_dir:  # User canceled the file dialog
        print("Operation aborted.")
        return

    id3_tags = {}
    for file_name in os.listdir(files_dir):
        file_path = os.path.join(files_dir, file_name)
        if file_name.lower().endswith('.mp3'):
            id3_tags[file_name] = read_id3_tags(file_path)

    if not id3_tags:
        print("No MP3 files found in the selected directory.")
        return

    # Remove rare characters and '\r' from Genre tag and update 'genre' values in files
    genres = create_genre_folders(files_dir, id3_tags)

    # Prompt user to continue before moving files
    proceed = input("Do you want to continue? (yes/no): ")
    if proceed.lower() != 'yes':
        print("Operation aborted.")
        return

    # Move files to corresponding Genre folders
    files_moved, error_files, genre_files = move_files_to_genre_folders(files_dir, id3_tags, genres)
    print("Files moved successfully.")

    # Print statistics
    print("\nStatistics:")
    print(f"Total folders created: {len(genres)}")
    print(f"Total files moved: {files_moved}")
    print(f"Total files moved to error folder: {error_files}")
    for genre, count in genre_files.items():
        print(f"Total files moved to {genre} folder: {count}")

    root.mainloop()  # Start the Tkinter event loop

if __name__ == "__main__":
    main()
