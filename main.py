import tkinter as tk
from tkinter import ttk, messagebox
import yt_dlp
import threading
import os
import time

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
        self.root.geometry("700x620")
        self.root.resizable(False, False)
        self.placeholder = placeholder

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(
            self.root,
            text="YouTube Audio / Video Downloader",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        ttk.Label(self.root, text="Enter YouTube URLs (one per line):").pack(anchor="w", padx=20)
        self.url_text = tk.Text(self.root, height=8, width=80)
        self.url_text.pack(padx=20)
        ##placeholder text
        self.url_text.insert(tk.END, self.placeholder)

        # Buttons frame
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=8)

        self.fetch_btn = ttk.Button(btn_frame, text="Fetch Info", command=self.fetch_info)
        self.fetch_btn.grid(row=0, column=0, padx=5)

        self.download_type = tk.StringVar(value="video")

        ttk.Radiobutton(btn_frame, text="Video (MP4)", variable=self.download_type, value="video").grid(row=0, column=1, padx=5)
        ttk.Radiobutton(btn_frame, text="Audio (MP3)", variable=self.download_type, value="audio").grid(row=0, column=2, padx=5)

        self.download_btn = ttk.Button(btn_frame, text="Start Download", command=self.start_download)
        self.download_btn.grid(row=0, column=3, padx=5)

        # Metadata display
        ttk.Label(self.root, text="Video / Audio Info:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 0))

        self.info_box = tk.Text(self.root, height=8, width=80, state="disabled", bg="#f5f5f5")
        self.info_box.pack(padx=20, pady=5)

        # Status box
        ttk.Label(self.root, text="Status:").pack(anchor="w", padx=20)
        self.status_text = tk.Text(self.root, height=8, width=80, state="disabled")
        self.status_text.pack(padx=20, pady=5)

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

    def fetch_info(self):
        urls = self.url_text.get("1.0", tk.END).strip().splitlines()

        if not urls or urls == [""]:
            messagebox.showerror("Error", "Please enter at least one YouTube URL.")
            return

        # Only fetch info for the first URL
        url = urls[0].strip()
        self.fetch_btn.config(state="disabled")
        self.set_info("Fetching video information...\n")

        threading.Thread(target=self._fetch_info_thread, args=(url,), daemon=True).start()

    def _fetch_info_thread(self, url):
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            title = info.get("title", "Unknown")
            duration = format_duration(info.get("duration"))
            views = f"{info.get('view_count', 0):,}"
            likes = info.get("like_count", "Not available")
            uploader = info.get("uploader", "Unknown")

            text = (
                f"Title: {title}\n"
                f"Duration: {duration}\n"
                f"Views: {views}\n"
                f"Likes: {likes}\n"
                f"Dislikes: Not available\n"
                f"Channel: {uploader}\n"
            )

            self.root.after(0, self.set_info, text)

        except Exception as e:
            self.root.after(0, self.set_info, f"Failed to fetch info:\n{str(e)}")

        finally:
            self.root.after(0, lambda: self.fetch_btn.config(state="normal"))

    def start_download(self):
        urls = self.url_text.get("1.0", tk.END).strip().splitlines()

        if not urls or urls == [""]:
            messagebox.showerror("Error", "Please enter at least one YouTube URL.")
            return

        self.download_btn.config(state="disabled")
        self.log_status("Starting downloads...\n")

        threading.Thread(target=self.download_batch, args=(urls,), daemon=True).start()

    def download_batch(self, urls):
        for url in urls:
            url = url.strip()
            if not url:
                continue

            try:
                self.log_status(f"Processing: {url}")

                if self.download_type.get() == "audio":
                    ydl_opts = {
                        "format": "bestaudio/best",
                        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
                        "postprocessors": [{
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }],
                        "quiet": True,
                        "no_warnings": True,
                    }
                else:
                    ydl_opts = {
                        "format": "bestvideo+bestaudio/best",
                        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
                        "merge_output_format": "mp4",
                        "quiet": True,
                        "no_warnings": True,
                    }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    title = info.get("title", "Unknown")
                    self.log_status(f"✅ Downloaded: {title}")

            except Exception as e:
                self.log_status(f"❌ Error: {str(e)}")

        self.log_status("\nAll downloads finished.")
        self.download_btn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
