import os
import eyed3
import tkinter as tk
from tkinter import filedialog
import datetime
import re

def select_folder():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    folder_path = filedialog.askdirectory(title="Select Folder Containing MP3 Files")
    return folder_path

def separate_session_number(filename):
    # Using regular expression to separate the word "session" and the number from the filename
    match = re.search(r'session(\d+)', filename, re.IGNORECASE)
    if match:
        word = filename[:match.start()]
        number = match.group(1)
        return word, number
    else:
        return filename, None

def convert_date_format(date_str):
    # Convert date format from YYYYMMDD to DD.MM.YYYY
    try:
        date = datetime.datetime.strptime(date_str, '%Y%m%d').date()
        return date.strftime("%d.%m.%Y")
    except ValueError:
        print(f"Invalid date format: {date_str}")
        return None

def process_files(folder_path):
    # Iterate over files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mp3'):
            file_path = os.path.join(folder_path, file_name)
            # Extract first 8 characters of the file name as YYYYMMDD
            date_str = file_name[:8]
            converted_date_str = convert_date_format(date_str)
            if converted_date_str is None:
                continue

            # Load the audio file
            audiofile = eyed3.load(file_path)
            if audiofile is not None:
                # Separate "session" and number from the file name if present
                title, session_number = separate_session_number(file_name[8:].replace('_', ' ').lower())
                # Update Title ID3 tag to uppercase
                title = title.upper()
                # Add session number to title if it exists
                if session_number:
                    title += f" Session {session_number}"
                audiofile.tag.title = title

                # Update the creation date file attribute
                creation_date = datetime.datetime.strptime(converted_date_str, '%d.%m.%Y')
                os.utime(file_path, (creation_date.timestamp(), creation_date.timestamp()))

                # Update Date ID3 tag
                audiofile.tag.date = converted_date_str

                # Update Comment ID3 tag
                comment = f"Session recorded the {converted_date_str}"
                audiofile.tag.comments.set(comment)

                # Save changes
                audiofile.tag.save()

                # Rename the file
                new_file_name = title.lstrip('_').replace(' ', '_') + '.mp3'
                new_file_path = os.path.join(folder_path, new_file_name)
                os.rename(file_path, new_file_path)

                print(f"Updated ID3 tag and renamed file to {new_file_name}: Title changed to '{title}', Date set to '{converted_date_str}', Comment updated.")

if __name__ == "__main__":
    folder_path = select_folder()
    if folder_path:
        process_files(folder_path)
