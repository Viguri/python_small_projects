import os
import hashlib
from collections import defaultdict
from tkinter import filedialog, Tk
from tqdm import tqdm
import multiprocessing

def get_hash(filepath):
    """Generate a SHA-256 hash of the file."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(65536)  # Read in 64k chunks
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

def find_duplicates_in_directory(directory):
    """Find duplicated MP3 or FLAC files based on file names."""
    duplicates = defaultdict(list)
    total_files = sum(len(files) for _, _, files in os.walk(directory))
    progress = tqdm(total=total_files, desc=f"Processing {directory}", unit="files", position=0, leave=False)
    for root, dirs, files in os.walk(directory):
        # Only search in directories that start with '_'
        dirs[:] = [d for d in dirs]
        for file in files:
            if file.lower().endswith(('.mp3', '.flac')):
                file_path = os.path.join(root, file)
                hash_value = get_hash(file_path)
                duplicates[(file, hash_value)].append(file_path)
                progress.update(1)
    progress.close()
    return duplicates

def find_duplicates(folder_path):
    pool = multiprocessing.Pool()
    results = pool.map(find_duplicates_in_directory, [folder_path])
    pool.close()
    pool.join()

    duplicates = {}
    for result in results:
        duplicates.update(result)
    return duplicates

def write_statistics(duplicates, output_file):
    """Write statistics of duplicated files to a file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Duplicate Files:\n")
        for key, value in duplicates.items():
            f.write(f"File Name: {key[0]}, Hash: {key[1]}\n")
            for file in value:
                f.write(f"\t{file}\n")
            f.write("\n")
        f.write(f"Total Duplicates: {sum(len(files) for files in duplicates.values())}\n")

def main():
    # Prompt for folder using tkinter dialog
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Folder to Search")

    if folder_path:
        duplicates = find_duplicates(folder_path)
        if duplicates:
            output_file = "duplicates_statistics.txt"
            write_statistics(duplicates, output_file)
            print(f"Statistics written to {output_file}")
        else:
            print("No duplicates found.")

if __name__ == "__main__":
    main()
