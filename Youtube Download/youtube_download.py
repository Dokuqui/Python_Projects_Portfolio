import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import subprocess
import threading
import re

def validate_url(url):
    youtube_regex = r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+"
    if not re.match(youtube_regex, url):
        messagebox.showwarning("Attention", "Invalid YouTube URL. Please enter a valid YouTube video link.")
        return False
    return True

def select_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        destination_folder_entry.delete(0, tk.END)
        destination_folder_entry.insert(0, folder_selected)

def enable_ui():
    download_button.config(state=tk.NORMAL)
    browse_button.config(state=tk.NORMAL)
    format_combo.config(state="readonly")
    url_entry.config(state=tk.NORMAL)
    destination_folder_entry.config(state=tk.NORMAL)

def disable_ui():
    download_button.config(state=tk.DISABLED)
    browse_button.config(state=tk.DISABLED)
    format_combo.config(state=tk.DISABLED)
    url_entry.config(state=tk.DISABLED)
    destination_folder_entry.config(state=tk.DISABLED)

def download_video():
    disable_ui()
    log_output.delete(1.0, tk.END)
    url = url_entry.get().strip()
    if not validate_url(url):
        enable_ui()
        return

    dest = destination_folder_entry.get().strip()
    if not dest:
        messagebox.showwarning("Attention", "Please select a destination folder.")
        enable_ui()
        return

    selected_format = format_var.get()

    if selected_format == "MP3 (Audio only)":
        cmd = [
            "yt-dlp", url,
            "-P", dest,
            "-f", "bestaudio",
            "-x", "--audio-format", "mp3",
            "--audio-quality", "0",
            "--embed-metadata",
            "--embed-thumbnail",
            "--newline"
        ]
    elif selected_format == "MP4 720p":
        cmd = [
            "yt-dlp", url,
            "-P", dest,
            "-f", "bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[ext=mp4]",
            "--merge-output-format", "mp4",
            "--embed-subs",
            "--embed-metadata",
            "--embed-thumbnail",
            "--newline"
        ]
    elif selected_format == "MP4 Best quality":
        cmd = [
            "yt-dlp", url,
            "-P", dest,
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
            "--merge-output-format", "mp4",
            "--embed-subs",
            "--embed-metadata",
            "--embed-thumbnail",
            "--newline"
        ]
    elif selected_format == "WebM Best quality":
        cmd = [
            "yt-dlp", url,
            "-P", dest,
            "-f", "bestvideo+bestaudio/best",
            "--embed-subs",
            "--embed-metadata",
            "--newline"
        ]
    else:
        messagebox.showerror("Error", "Unknown format selected.")
        enable_ui()
        return

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        progress_bar["value"] = 0
        root.update()

        for line in process.stdout:
            log_output.insert(tk.END, line)
            log_output.see(tk.END)
            if "[download]" in line and "%" in line:
                try:
                    percent = float(line.split("%")[0].split()[-1])
                    progress_bar["value"] = percent
                    root.update()
                except Exception:
                    pass

        ret = process.wait()
        if ret == 0:
            messagebox.showinfo("Success", "Download complete.")
        else:
            messagebox.showerror("yt-dlp Failed", f"Process exited with code {ret}")

    except Exception as e:
        messagebox.showerror("Error", str(e))
    enable_ui()

def start_download():
    threading.Thread(target=download_video, daemon=True).start()

# GUI
root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("600x420")
root.resizable(False, False)

tk.Label(root, text="Enter YouTube URL:").grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
url_entry = tk.Entry(root, width=60)
url_entry.grid(row=0, column=1, padx=10, pady=5, columnspan=2)

tk.Label(root, text="Select Destination Folder:").grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
destination_folder_entry = tk.Entry(root, width=50)
destination_folder_entry.grid(row=1, column=1, padx=10, pady=5)
browse_button = tk.Button(root, text="Browse", command=select_folder)
browse_button.grid(row=1, column=2, padx=5, pady=5)

tk.Label(root, text="Select Format:").grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
format_var = tk.StringVar()
format_combo = ttk.Combobox(root, textvariable=format_var, width=45, state="readonly")
format_combo["values"] = [
    "MP3 (Audio only)",
    "MP4 720p",
    "MP4 Best quality",
    "WebM Best quality"
]
format_combo.current(1)
format_combo.grid(row=2, column=1, padx=10, pady=5, columnspan=2)

download_button = tk.Button(root, text="Download", command=start_download, width=20)
download_button.grid(row=3, column=0, columnspan=3, pady=10)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=560, mode="determinate")
progress_bar.grid(row=4, column=0, columnspan=3, padx=10, pady=(5, 5))

tk.Label(root, text="Output Log:").grid(row=5, column=0, columnspan=3, sticky=tk.W, padx=10)
log_output = tk.Text(root, height=10, width=74, wrap=tk.WORD)
log_output.grid(row=6, column=0, columnspan=3, padx=10, pady=(0, 10))

root.mainloop()
