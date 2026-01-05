import tkinter as tk
from tkinter import ttk, messagebox
import yt_dlp
import threading
import os
from PIL import Image, ImageTk
import urllib.request
import io

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def format_duration(seconds):
    if not seconds:
        return "Unknown"
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    if hours:
        return f"{hours}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


class YouTubeDownloaderApp:
    def __init__(self, root, placeholder="Enter YouTube URLs here..."):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("700x680")
        self.root.resizable(False, False)

        self.placeholder = placeholder
        self.thumbnail_img = None

        self.create_widgets()

    # ------------------ Thumbnail ------------------
    def set_thumbnail(self, url=None):
        if not url:
            self.thumbnail_label.config(image="")
            return

        try:
            with urllib.request.urlopen(url) as u:
                raw_data = u.read()

            image = Image.open(io.BytesIO(raw_data))
            image = image.resize((200, 120), Image.LANCZOS)

            self.thumbnail_img = ImageTk.PhotoImage(image)
            self.thumbnail_label.config(image=self.thumbnail_img)

        except Exception:
            self.thumbnail_label.config(image="")

    # ------------------ Progress ------------------
    def progress_hook(self, d):
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%").replace("%", "").strip()
            speed = d.get("_speed_str", "--")
            eta = d.get("_eta_str", "--")

            try:
                percent_float = float(percent)
            except ValueError:
                percent_float = 0.0

            self.root.after(0, lambda: self.progress_var.set(percent_float))
            self.root.after(0, lambda: self.progress_label.config(
                text=f"Progress: {percent_float:.1f}%"
            ))
            self.root.after(0, lambda: self.speed_label.config(text=f"Speed: {speed}"))
            self.root.after(0, lambda: self.eta_label.config(text=f"ETA: {eta}"))

        elif d["status"] == "finished":
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.progress_label.config(text="Progress: 100%"))
            self.root.after(0, lambda: self.speed_label.config(text="Speed: Done"))
            self.root.after(0, lambda: self.eta_label.config(text="ETA: 0s"))

    def reset_progress(self):
        self.progress_var.set(0)
        self.progress_label.config(text="Progress: 0%")
        self.speed_label.config(text="Speed: --")
        self.eta_label.config(text="ETA: --")

    # ------------------ UI ------------------
    def create_widgets(self):
        ttk.Label(
            self.root,
            text="YouTube Audio / Video Downloader",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        ttk.Label(self.root, text="Enter YouTube URLs (one per line):").pack(anchor="w", padx=20)

        self.url_text = tk.Text(self.root, height=8, width=80)
        self.url_text.pack(padx=20)
        self.url_text.insert(tk.END, self.placeholder)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=8)

        self.fetch_btn = ttk.Button(btn_frame, text="Fetch Info", command=self.fetch_info)
        self.fetch_btn.grid(row=0, column=0, padx=5)

        self.download_type = tk.StringVar(value="video")

        ttk.Radiobutton(
            btn_frame, text="Video (MP4)",
            variable=self.download_type, value="video"
        ).grid(row=0, column=1, padx=5)

        ttk.Radiobutton(
            btn_frame, text="Audio (MP3)",
            variable=self.download_type, value="audio"
        ).grid(row=0, column=2, padx=5)

        self.download_btn = ttk.Button(
            btn_frame, text="Start Download", command=self.start_download
        )
        self.download_btn.grid(row=0, column=3, padx=5)

        # Thumbnail preview
        thumb_frame = ttk.Frame(self.root)
        thumb_frame.pack(padx=20, pady=5, anchor="w")

        self.thumbnail_label = ttk.Label(thumb_frame)
        self.thumbnail_label.pack()

        # Progress
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(pady=10, padx=20, fill="x")

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(fill="x")

        self.progress_label = ttk.Label(progress_frame, text="Progress: 0%")
        self.progress_label.pack(anchor="w")

        self.speed_label = ttk.Label(progress_frame, text="Speed: --")
        self.speed_label.pack(anchor="w")

        self.eta_label = ttk.Label(progress_frame, text="ETA: --")
        self.eta_label.pack(anchor="w")

        # Info
        ttk.Label(
            self.root, text="Video / Audio Info:",
            font=("Arial", 12, "bold")
        ).pack(anchor="w", padx=20, pady=(10, 0))

        self.info_box = tk.Text(
            self.root, height=8, width=80,
            state="disabled", bg="#f5f5f5"
        )
        self.info_box.pack(padx=20, pady=5)

        # Status
        ttk.Label(self.root, text="Status:").pack(anchor="w", padx=20)
        self.status_text = tk.Text(
            self.root, height=8, width=80, state="disabled"
        )
        self.status_text.pack(padx=20, pady=5)

    # ------------------ Helpers ------------------
    def log_status(self, msg):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, msg + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")

    def set_info(self, info):
        self.info_box.config(state="normal")
        self.info_box.delete("1.0", tk.END)
        self.info_box.insert(tk.END, info)
        self.info_box.config(state="disabled")

    # ------------------ Fetch Info ------------------
    def fetch_info(self):
        urls = self.url_text.get("1.0", tk.END).strip().splitlines()
        if not urls:
            messagebox.showerror("Error", "Please enter at least one YouTube URL.")
            return

        self.fetch_btn.config(state="disabled")
        self.set_info("Fetching video information...\n")

        threading.Thread(
            target=self._fetch_info_thread,
            args=(urls[0].strip(),),
            daemon=True
        ).start()

    def _fetch_info_thread(self, url):
        try:
            with yt_dlp.YoutubeDL({
                "quiet": True,
                "no_warnings": True,
                "skip_download": True
            }) as ydl:
                info = ydl.extract_info(url, download=False)

            text = (
                f"Title: {info.get('title', 'Unknown')}\n"
                f"Duration: {format_duration(info.get('duration'))}\n"
                f"Views: {info.get('view_count', 0):,}\n"
                f"Likes: {info.get('like_count', 'N/A')}\n"
                f"Dislikes: {info.get('dislike_count', 'N/A')}\n"
                f"Channel: {info.get('uploader', 'Unknown')}\n"
            )

            self.root.after(0, self.set_info, text)
            self.root.after(0, self.set_thumbnail, info.get("thumbnail"))

        except Exception as e:
            self.root.after(0, self.set_info, f"Failed to fetch info:\n{e}")
            self.root.after(0, self.set_thumbnail, None)

        finally:
            self.root.after(0, lambda: self.fetch_btn.config(state="normal"))

    # ------------------ Download ------------------
    def start_download(self):
        urls = self.url_text.get("1.0", tk.END).strip().splitlines()
        if not urls:
            messagebox.showerror("Error", "Please enter at least one YouTube URL.")
            return

        self.download_btn.config(state="disabled")
        self.log_status("Starting downloads...\n")

        threading.Thread(
            target=self.download_batch,
            args=(urls,),
            daemon=True
        ).start()

    def download_batch(self, urls):
        for url in urls:
            if not url.strip():
                continue

            try:
                self.log_status(f"Processing: {url}")
                self.root.after(0, self.reset_progress)

                if self.download_type.get() == "audio":
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
                        "writethumbnail": True,
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": "192",
                            },
                            {"key": "EmbedThumbnail"},
                            {"key": "FFmpegMetadata"},
                        ],
                        "progress_hooks": [self.progress_hook],
                        "quiet": True,
                        "no_warnings": True,
                    }
                else:
                    ydl_opts = {
                        "format": "bestvideo+bestaudio/best",
                        "merge_output_format": "mp4",
                        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
                        "writethumbnail": True,
                        "embedthumbnail": True,
                        "progress_hooks": [self.progress_hook],
                        "quiet": True,
                        "no_warnings": True,
                    }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    self.log_status(f"✅ Downloaded: {info.get('title', 'Unknown')}")

            except Exception as e:
                self.log_status(f"❌ Error: {e}")

        self.log_status("\nAll downloads finished.")
        self.root.after(0, lambda: self.download_btn.config(state="normal"))


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
