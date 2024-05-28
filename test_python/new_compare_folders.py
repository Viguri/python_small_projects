import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

def collect_file_data(directory, file_data, lock):
    for root, _, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            file_info = (file, path)  # Store both file name and path
            with lock:
                file_data.add(file_info)

def compare_and_copy_files(dir1, dir2, output_file):
    file_data_dir1 = set()
    file_data_dir2 = set()
    lock1 = threading.Lock()
    lock2 = threading.Lock()

    thread1 = threading.Thread(target=collect_file_data, args=(dir1, file_data_dir1, lock1))
    thread2 = threading.Thread(target=collect_file_data, args=(dir2, file_data_dir2, lock2))

    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    # Extract only the file names from dir2 for comparison
    file_names_dir2 = {name for name, _ in file_data_dir2}

    # Find unique files in dir1 based on file names
    unique_to_dir1 = {info for info in file_data_dir1 if info[0] not in file_names_dir2}

    # Prepare directory for unique files in dir2
    unique_dir = os.path.join(dir2, "UNIQUE")
    os.makedirs(unique_dir, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Files unique to " + dir1 + ":\n")
        for name, path in unique_to_dir1:
            f.write(f"{name} (Location: {path})\n")
            # Copy file to the UNIQUE subfolder in dir2
            shutil.copy(path, os.path.join(unique_dir, name))

    tk.messagebox.showinfo("Comparison Complete", f"Results written to {output_file}. Unique files copied to {unique_dir}")

def run_comparison():
    dir1 = filedialog.askdirectory(title="Select First Directory")
    dir2 = filedialog.askdirectory(title="Select Second Directory")
    if dir1 and dir2:
        output_file = filedialog.asksaveasfilename(title="Save Comparison Results As", filetypes=[("Text files", "*.txt")])
        if output_file:
            compare_thread = threading.Thread(target=compare_and_copy_files, args=(dir1, dir2, output_file))
            compare_thread.start()
        else:
            tk.messagebox.showerror("Error", "No output file selected.")
    else:
        tk.messagebox.showerror("Error", "Directory selection was cancelled.")

def create_gui():
    root = tk.Tk()
    root.title("Directory File Comparator")
    root.geometry("500x200")
    tk.Button(root, text="Select Directories and Compare", command=run_comparison).pack(pady=30)
    root.mainloop()

if __name__ == "__main__":
    create_gui()
