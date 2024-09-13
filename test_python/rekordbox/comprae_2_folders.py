import os
import tkinter as tk
from tkinter import filedialog

def compare_folders(folder1, folder2, output_file):
    file_list_a = []
    file_list_b = []
    
    # Counters for statistics
    files_in_a = 0
    files_in_b = 0

    # Walk through folder A
    for root, dirs, files in os.walk(folder1):
        # Filter out folders not starting with "_"
        dirs[:] = [d for d in dirs if d.startswith('_') or os.path.join(root, d) == folder1]
        for file in files:
            if file.endswith(('.mp3', '.flac')):
                file_path = os.path.relpath(os.path.join(root, file), folder1)
                file_list_a.append(file_path)
                files_in_a += 1
    
    # Walk through folder B
    for root, dirs, files in os.walk(folder2):
        for file in files:
            if file.endswith(('.mp3', '.flac')):
                file_list_b.append(os.path.relpath(os.path.join(root, file), folder2))
                files_in_b += 1

    # Compare the two lists
    files_only_in_b = set(file_list_b) - set(file_list_a)
    files_only_in_a = set(file_list_a) - set(file_list_b)

    # Write results to file with UTF-8 encoding
    with open(os.path.join(folder1, output_file), 'w', encoding='utf-8') as f:
        f.write("Files found in Folder A: {}\n".format(files_in_a))
        f.write("Files found in Folder B: {}\n".format(files_in_b))
        f.write("Files in Folder B but not in Folder A: {}\n".format(len(files_only_in_b)))
        f.write("Files in Folder A but not in Folder B: {}\n".format(len(files_only_in_a)))
        f.write("\nFiles in Folder B but not in Folder A:\n")
        for file in files_only_in_b:
            f.write(file + '\n')
        f.write("\nFiles in Folder A but not in Folder B:\n")
        for file in files_only_in_a:
            f.write(file + '\n')
        f.write("\nFiles in both Folder A and Folder B:\n")
        for file in set(file_list_a) & set(file_list_b):
            f.write(file + '\n')

def select_folder(label):
    folder_path = filedialog.askdirectory(title=label)
    return folder_path

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    # Select Folder A
    folder_a = select_folder("Select Folder A")
    if not folder_a:
        print("Folder A selection canceled.")
        return

    # Select Folder B
    folder_b = select_folder("Select Folder B")
    if not folder_b:
        print("Folder B selection canceled.")
        return

    output_file = "comparison_results.txt"
    compare_folders(folder_a, folder_b, output_file)
    print("Comparison completed. Results written to", os.path.join(folder_a, output_file))

if __name__ == "__main__":
    main()