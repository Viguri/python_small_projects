import tkinter as tk
from tkinter import filedialog
import librosa
import numpy as np

def load_waveform(file_path):
    y, sr = librosa.load(file_path, sr=None)
    return y, sr

def compare_waveforms(waveform1, waveform2):
    # Make sure waveforms are the same length
    min_length = min(len(waveform1), len(waveform2))
    waveform1 = waveform1[:min_length]
    waveform2 = waveform2[:min_length]
    
    # Normalize waveforms
    waveform1 = waveform1 / np.linalg.norm(waveform1)
    waveform2 = waveform2 / np.linalg.norm(waveform2)
    
    # Calculate similarity (e.g., cosine similarity)
    similarity = np.dot(waveform1, waveform2)
    return similarity

def select_files():
    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Open file dialog to select two files
    file_paths = filedialog.askopenfilenames(title="Select Two Audio Files", filetypes=[("Audio Files", "*.mp3;*.wav;*.flac")])
    
    # Ensure exactly two files are selected
    if len(file_paths) != 2:
        print("Please select exactly two audio files.")
        return None, None
    
    return file_paths[0], file_paths[1]

def main():
    file1, file2 = select_files()
    if not file1 or not file2:
        return

    waveform1, sr1 = load_waveform(file1)
    waveform2, sr2 = load_waveform(file2)

    similarity = compare_waveforms(waveform1, waveform2)
    print(f'Similarity: {similarity}')

if __name__ == "__main__":
    main()
