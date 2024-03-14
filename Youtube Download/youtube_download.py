import tkinter as tk
import os
from tkinter import messagebox, ttk
from pytube import YouTube


# Validation of correct url
def validate_url(url):
    if not url.startswith("https://www.youtube.com/watch?v="):
        messagebox.showwarning("Attention", "Invalid YouTube URL. Please enter a valid YouTube video link. "
                                            "It should start with https://www.youtube.com/watch?")
        return False
    return True


# Function to upload one video or audio
def download_video(audio_only=False):
    url = url_entry.get()

    # Validate url
    if not validate_url(url):
        return False

    try:
        yt = YouTube(url)
        audio_only = audio_only_var.get()
        if audio_only:
            stream = yt.streams.filter(only_audio=True).first()
        else:
            stream = yt.streams.get_highest_resolution()
        destination_folder = destination_folder_entry.get()
        file_path = stream.download(output_path=destination_folder)

        # Determine size of file
        total_size = os.path.getsize(file_path)

        # Open the downloaded file and stream it to the buffer, while updating the progress bar
        with open(file_path, "rb") as file:
            bytes_received = 0
            chunk_size = 1024
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                bytes_received += len(chunk)
                progress = int(bytes_received / total_size * 100)
                progress_bar["value"] = progress
                root.update()

        # Show message based on the mode
        if audio_only:
            messagebox.showinfo("Download Complete", "Audio Downloaded Successfully")
        else:
            messagebox.showinfo("Download Complete", "Video Downloaded Successfully")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while downloading: {e}")


# Create the main window
root = tk.Tk()
root.title("Youtube Downloader")
root.geometry("500x200")

# Create UI element
url_label = tk.Label(root, text="Enter YouTube URL: ")
url_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=5)

destination_folder_label = tk.Label(root, text="Enter Destination Folder: ")
destination_folder_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)

destination_folder_entry = tk.Entry(root, width=50)
destination_folder_entry.grid(row=1, column=1, padx=10, pady=5)

audio_only_var = tk.BooleanVar()
audio_only_checkbox = tk.Checkbutton(root, text="Download Audio Only", variable=audio_only_var)
audio_only_checkbox.grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)

download_button = tk.Button(root, text="Download", command=download_video)
download_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=2, padx=10, pady=(10, 5))


# Start the application
root.mainloop()
