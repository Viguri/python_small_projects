import csv
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import tkinter.messagebox as messagebox

# Function to select the input file
def select_input_file():
    # Hide the root window
    Tk().withdraw()
    
    # Open file dialog to select the file
    file_path = askopenfilename(title="Select the Exported Playlist File", filetypes=[("Text files", "*.txt")])
    
    if not file_path:
        raise FileNotFoundError("No file selected. Please select a file.")
    
    return file_path

# Function to read file in binary mode and decode manually
def read_file_binary(file_path):
    with open(file_path, mode='rb') as binary_file:
        raw_data = binary_file.read()
        try:
            # Try to decode using utf-8
            return raw_data.decode('utf-8')
        except UnicodeDecodeError:
            try:
                # Fallback to utf-16 if utf-8 fails
                return raw_data.decode('utf-16')
            except UnicodeDecodeError:
                # Fallback to ISO-8859-1 if utf-16 fails
                return raw_data.decode('iso-8859-1')

# Main function
def create_playlist():
    try:
        # Step 1: Select the input file
        input_file = select_input_file()

        # Step 2: Set the output file name (same as input but with .m3u extension)
        output_file = os.path.splitext(input_file)[0] + '.m3u'

        # Step 3: Check if output file exists
        if os.path.exists(output_file):
            # Ask the user if they want to overwrite the file
            overwrite = messagebox.askyesno("Overwrite Confirmation", f"The file '{output_file}' already exists. Do you want to overwrite it?")
            if not overwrite:
                print("Operation cancelled. The output file was not overwritten.")
                return
        
        # Step 4: Read the input file in binary mode and decode it
        file_content = read_file_binary(input_file)

        # Step 5: Create the M3U file
        with open(output_file, mode='w', encoding='utf-8') as m3u_file:
            # Write M3U header
            m3u_file.write("#EXTM3U\n")

            # Read the file content as CSV
            reader = csv.DictReader(file_content.splitlines(), delimiter='\t')
            reader.fieldnames = [field.strip() for field in reader.fieldnames]  # Strip whitespace

            # Step 6: Write each track to the M3U file with key information
            for row in reader:
                track_title = row['Track Title']
                artist = row['Artist']
                key = row['Key']
                time = row['Time']
                location = row['Location']
                
                # Write track info with key to M3U format
                m3u_file.write(f"#EXTINF:-1,{artist} - {track_title} [Key: {key}], {time}\n")
                m3u_file.write(f"{location}\n")
        
        print(f"Playlist with keys created successfully: {output_file}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the main function
if __name__ == "__main__":
    create_playlist()
