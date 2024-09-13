import os
from tkinter import Tk, filedialog

def remove_leading_underscores(folder_path):
    # List all files in the folder
    files = os.listdir(folder_path)
    
    # Filter out only MP3 files
    mp3_files = [file for file in files if file.lower().endswith('.mp3')]
    
    # Rename files with leading underscores removed
    for file in mp3_files:
        new_name = file.lstrip('_')
        if new_name != file:
            os.rename(os.path.join(folder_path, file), os.path.join(folder_path, new_name))
            print(f"Renamed '{file}' to '{new_name}'")

def select_folder():
    root = Tk()
    root.withdraw()  # Hide the root window
    folder_path = filedialog.askdirectory(title="Select Folder Containing MP3 Files")
    root.destroy()  # Destroy the root window after selection
    return folder_path

def main():
    folder_path = select_folder()
    if folder_path:
        remove_leading_underscores(folder_path)
        print("Leading underscores removed from MP3 files in the selected folder.")

if __name__ == "__main__":
    main()
