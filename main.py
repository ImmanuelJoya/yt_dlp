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


def format_number(num):
    if num is None:
        return "N/A"
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)

        self.dark_mode = True
        self.thumbnail_img = None
        self.video_info = None
        
        self.create_widgets()
        self.apply_theme()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            bg = "#0f0f0f"
            card_bg = "#1a1a1a"
            card_hover = "#222222"
            fg = "#ffffff"
            fg_secondary = "#9ca3af"
            accent = "#3b82f6"
            accent_hover = "#2563eb"
            success = "#10b981"
            border = "#2a2a2a"
            input_bg = "#262626"
        else:
            bg = "#ffffff"
            card_bg = "#f8fafc"
            card_hover = "#e2e8f0"
            fg = "#0f172a"
            fg_secondary = "#64748b"
            accent = "#2563eb"
            accent_hover = "#1e40af"
            success = "#059669"
            border = "#cbd5e1"
            input_bg = "#ffffff"

        self.root.configure(bg=bg)
        
        # Update all backgrounds
        for frame in [self.main_frame, self.header_frame, self.content_frame, self.left_panel, self.right_panel]:
            frame.configure(bg=bg)
        
        for card in [self.url_card, self.controls_card, self.thumbnail_card, self.info_card, self.stats_card, self.progress_card, self.status_card]:
            card.configure(bg=card_bg)
        
        # Update labels
        self.title_label.configure(bg=bg, fg=fg)
        self.subtitle_label.configure(bg=bg, fg=fg_secondary)
        
        for label in [self.url_label, self.controls_label, self.thumb_label, self.info_label, self.stats_label, self.progress_title]:
            label.configure(bg=card_bg, fg=fg)
        
        # Update entry
        self.url_entry.configure(bg=input_bg, fg=fg, insertbackground=fg)
        
        # Update buttons
        self.fetch_btn.configure(bg=accent, activebackground=accent_hover)
        self.download_btn.configure(bg=success, activebackground="#059669")
        self.video_btn.configure(
            bg=accent if self.download_type.get() == "video" else input_bg,
            fg="white" if self.download_type.get() == "video" else fg_secondary
        )
        self.audio_btn.configure(
            bg=accent if self.download_type.get() == "audio" else input_bg,
            fg="white" if self.download_type.get() == "audio" else fg_secondary
        )
        
        # Update theme toggle
        self.theme_label.configure(bg=bg, fg=fg_secondary)
        theme_text = "Light Mode" if self.dark_mode else "Dark Mode"
        theme_icon = "☀️" if self.dark_mode else "🌙"
        self.theme_btn.configure(text=f"{theme_icon} {theme_text}", bg=input_bg, fg=fg, activebackground=card_hover)
        
        # Update info display
        self.thumbnail_label.configure(bg=card_bg)
        self.video_title.configure(bg=card_bg, fg=fg)
        self.video_channel.configure(bg=card_bg, fg=fg_secondary)
        self.video_duration.configure(bg=card_bg, fg=fg_secondary)
        
        # Update stats
        for widget in [self.views_value, self.likes_value, self.comments_value, 
        self.views_label, self.likes_label, self.comments_label]:
            widget.configure(bg=card_bg)
        self.views_value.configure(fg=fg)
        self.likes_value.configure(fg=fg)
        self.comments_value.configure(fg=fg)
        self.views_label.configure(fg=fg_secondary)
        self.likes_label.configure(fg=fg_secondary)
        self.comments_label.configure(fg=fg_secondary)
        
        # Update progress
        self.progress_canvas.configure(bg=border)
        self.progress_percent.configure(bg=card_bg, fg=fg)
        self.progress_speed.configure(bg=card_bg, fg=fg_secondary)
        self.progress_eta.configure(bg=card_bg, fg=fg_secondary)
        
        # Update status
        self.status_text.configure(bg=input_bg, fg=fg, insertbackground=fg)

    def create_widgets(self):
        # Main container
        self.main_frame = tk.Frame(self.root, bg="#0f0f0f")
        self.main_frame.pack(fill="both", expand=True)

        # Header
        self.header_frame = tk.Frame(self.main_frame, bg="#0f0f0f")
        self.header_frame.pack(fill="x", padx=40, pady=(30, 20))
        
        header_left = tk.Frame(self.header_frame, bg="#0f0f0f")
        header_left.pack(side="left")
        
        self.title_label = tk.Label(header_left, text="YouTube Downloader", 
                                    font=("Segoe UI", 26, "bold"), bg="#0f0f0f", fg="white")
        self.title_label.pack(anchor="w")
        
        self.subtitle_label = tk.Label(header_left, text="Download videos and audio in high quality", 
            font=("Segoe UI", 11), bg="#0f0f0f", fg="#9ca3af")
        self.subtitle_label.pack(anchor="w", pady=(2, 0))
        
        # Theme toggle in header
        header_right = tk.Frame(self.header_frame, bg="#0f0f0f")
        header_right.pack(side="right")
        
        self.theme_label = tk.Label(header_right, text="Appearance", 
                                    font=("Segoe UI", 9), bg="#0f0f0f", fg="#9ca3af")
        self.theme_label.pack(anchor="e")
        
        self.theme_btn = tk.Button(header_right, text="☀️ Light Mode", command=self.toggle_theme,
            bg="#262626", fg="white", font=("Segoe UI", 10),
            relief="flat", borderwidth=0, cursor="hand2", 
            padx=15, pady=8, activebackground="#222222")
        self.theme_btn.pack(anchor="e", pady=(5, 0))

        # Content area
        self.content_frame = tk.Frame(self.main_frame, bg="#0f0f0f")
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=(0, 30))

        # Left Panel
        self.left_panel = tk.Frame(self.content_frame, bg="#0f0f0f")
        self.left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))

        # URL Input Card
        self.url_card = tk.Frame(self.left_panel, bg="#1a1a1a")
        self.url_card.pack(fill="x", pady=(0, 15))
        
        self.url_label = tk.Label(self.url_card, text="YouTube URL", 
            font=("Segoe UI", 11, "bold"), bg="#1a1a1a", fg="white", anchor="w")
        self.url_label.pack(fill="x", padx=20, pady=(15, 8))
        
        self.url_entry = tk.Entry(self.url_card, font=("Segoe UI", 12), 
            relief="flat", borderwidth=0, bg="#262626", fg="white")
        self.url_entry.pack(fill="x", padx=20, pady=(0, 15), ipady=12)
        self.url_entry.insert(0, "https://www.youtube.com/watch?v=...")

        # Controls Card
        self.controls_card = tk.Frame(self.left_panel, bg="#1a1a1a")
        self.controls_card.pack(fill="x", pady=(0, 15))
        
        self.controls_label = tk.Label(self.controls_card, text="Download Options", 
            font=("Segoe UI", 11, "bold"), bg="#1a1a1a", fg="white", anchor="w")
        self.controls_label.pack(fill="x", padx=20, pady=(15, 12))
        
        controls_inner = tk.Frame(self.controls_card, bg="#1a1a1a")
        controls_inner.pack(fill="x", padx=20, pady=(0, 15))
        
        # Download type
        self.download_type = tk.StringVar(value="video")
        
        type_label = tk.Label(controls_inner, text="Format:", font=("Segoe UI", 10), 
            bg="#1a1a1a", fg="#9ca3af")
        type_label.pack(anchor="w", pady=(0, 8))
        
        type_frame = tk.Frame(controls_inner, bg="#1a1a1a")
        type_frame.pack(fill="x", pady=(0, 15))
        
        self.video_btn = tk.Button(type_frame, text="🎬 Video (MP4)", 
            command=lambda: self.set_download_type("video"),
            bg="#3b82f6", fg="white", font=("Segoe UI", 10, "bold"),
            relief="flat", borderwidth=0, cursor="hand2", 
            padx=20, pady=10, width=15, anchor="w")
        self.video_btn.pack(side="left", padx=(0, 10))
        
        self.audio_btn = tk.Button(type_frame, text="🎵 Audio (MP3)", 
            command=lambda: self.set_download_type("audio"),
            bg="#262626", fg="#9ca3af", font=("Segoe UI", 10, "bold"),
            relief="flat", borderwidth=0, cursor="hand2", 
            padx=20, pady=10, width=15, anchor="w")
        self.audio_btn.pack(side="left")
        
        # Action buttons
        action_frame = tk.Frame(controls_inner, bg="#1a1a1a")
        action_frame.pack(fill="x")
        
        self.fetch_btn = tk.Button(action_frame, text="📥 Fetch Info", command=self.fetch_info,
            bg="#3b82f6", fg="white", font=("Segoe UI", 11, "bold"),
            relief="flat", borderwidth=0, cursor="hand2", 
            padx=25, pady=12, activebackground="#2563eb")
        self.fetch_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        self.download_btn = tk.Button(action_frame, text="⬇️ Download", command=self.start_download,
            bg="#10b981", fg="white", font=("Segoe UI", 11, "bold"),
        relief="flat", borderwidth=0, cursor="hand2", 
            padx=25, pady=12, activebackground="#059669")
        self.download_btn.pack(side="left", fill="x", expand=True)

        # Progress Card
        self.progress_card = tk.Frame(self.left_panel, bg="#1a1a1a")
        self.progress_card.pack(fill="x", pady=(0, 15))
        
        self.progress_title = tk.Label(self.progress_card, text="Download Progress", 
            font=("Segoe UI", 11, "bold"), bg="#1a1a1a", fg="white", anchor="w")
        self.progress_title.pack(fill="x", padx=20, pady=(15, 12))
        
        progress_inner = tk.Frame(self.progress_card, bg="#1a1a1a")
        progress_inner.pack(fill="x", padx=20, pady=(0, 15))
        
        self.progress_var = tk.DoubleVar()
        
        # Progress bar
        self.progress_canvas = tk.Canvas(progress_inner, height=8, bg="#2a2a2a",
                                        highlightthickness=0)
        self.progress_canvas.pack(fill="x", pady=(0, 10))
        
        self.progress_fill = self.progress_canvas.create_rectangle(0, 0, 0, 8, fill="#3b82f6", outline="")
        
        # Progress info
        progress_info = tk.Frame(progress_inner, bg="#1a1a1a")
        progress_info.pack(fill="x")
        
        self.progress_percent = tk.Label(progress_info, text="0%", 
                                        font=("Segoe UI", 10, "bold"), bg="#1a1a1a", fg="white")
        self.progress_percent.pack(side="left")
        
        self.progress_speed = tk.Label(progress_info, text="", 
            font=("Segoe UI", 9), bg="#1a1a1a", fg="#9ca3af")
        self.progress_speed.pack(side="right")
        
        self.progress_eta = tk.Label(progress_info, text="", 
                                    font=("Segoe UI", 9), bg="#1a1a1a", fg="#9ca3af")
        self.progress_eta.pack(side="right", padx=(0, 15))

        # Status Card
        self.status_card = tk.Frame(self.left_panel, bg="#1a1a1a")
        self.status_card.pack(fill="both", expand=True)
        
        status_label = tk.Label(self.status_card, text="Status Log", 
            font=("Segoe UI", 11, "bold"), bg="#1a1a1a", fg="white", anchor="w")
        status_label.pack(fill="x", padx=20, pady=(15, 10))
        
        self.status_text = tk.Text(self.status_card, height=6, font=("Consolas", 9),
            relief="flat", borderwidth=0, bg="#262626", fg="white",
            state="disabled", wrap="word")
        self.status_text.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Right Panel
        self.right_panel = tk.Frame(self.content_frame, bg="#0f0f0f", width=400)
        self.right_panel.pack(side="right", fill="both")
        self.right_panel.pack_propagate(False)

        # Thumbnail Card
        self.thumbnail_card = tk.Frame(self.right_panel, bg="#1a1a1a")
        self.thumbnail_card.pack(fill="x", pady=(0, 15))
        
        self.thumb_label = tk.Label(self.thumbnail_card, text="Preview", 
            font=("Segoe UI", 11, "bold"), bg="#1a1a1a", fg="white", anchor="w")
        self.thumb_label.pack(fill="x", padx=20, pady=(15, 12))
        
        self.thumbnail_label = tk.Label(self.thumbnail_card, bg="#1a1a1a", 
            text="No thumbnail", fg="#6b7280")
        self.thumbnail_label.pack(pady=(0, 15))

        # Info Card
        self.info_card = tk.Frame(self.right_panel, bg="#1a1a1a")
        self.info_card.pack(fill="x", pady=(0, 15))
        
        self.info_label = tk.Label(self.info_card, text="Video Information", 
            font=("Segoe UI", 11, "bold"), bg="#1a1a1a", fg="white", anchor="w")
        self.info_label.pack(fill="x", padx=20, pady=(15, 12))
        
        info_inner = tk.Frame(self.info_card, bg="#1a1a1a")
        info_inner.pack(fill="x", padx=20, pady=(0, 15))
        
        self.video_title = tk.Label(info_inner, text="No video loaded", 
            font=("Segoe UI", 11, "bold"), bg="#1a1a1a", fg="white",
            anchor="w", wraplength=340, justify="left")
        self.video_title.pack(fill="x", pady=(0, 8))
        
        self.video_channel = tk.Label(info_inner, text="Unknown channel", 
            font=("Segoe UI", 10), bg="#1a1a1a", fg="#9ca3af", anchor="w")
        self.video_channel.pack(fill="x", pady=(0, 4))
        
        self.video_duration = tk.Label(info_inner, text="Duration: --:--", 
            font=("Segoe UI", 10), bg="#1a1a1a", fg="#9ca3af", anchor="w")
        self.video_duration.pack(fill="x")

        # Stats Card
        self.stats_card = tk.Frame(self.right_panel, bg="#1a1a1a")
        self.stats_card.pack(fill="x")
        
        self.stats_label = tk.Label(self.stats_card, text="Statistics", 
            font=("Segoe UI", 11, "bold"), bg="#1a1a1a", fg="white", anchor="w")
        self.stats_label.pack(fill="x", padx=20, pady=(15, 12))
        
        stats_inner = tk.Frame(self.stats_card, bg="#1a1a1a")
        stats_inner.pack(fill="x", padx=20, pady=(0, 15))
        
        # Views
        views_box = tk.Frame(stats_inner, bg="#1a1a1a")
        views_box.pack(fill="x", pady=(0, 10))
        
        self.views_value = tk.Label(views_box, text="--", 
            font=("Segoe UI", 16, "bold"), bg="#1a1a1a", fg="white", anchor="w")
        self.views_value.pack(anchor="w")
        
        self.views_label = tk.Label(views_box, text="👁️ Views", 
            font=("Segoe UI", 9), bg="#1a1a1a", fg="#9ca3af", anchor="w")
        self.views_label.pack(anchor="w")
        
        # Likes
        likes_box = tk.Frame(stats_inner, bg="#1a1a1a")
        likes_box.pack(fill="x", pady=(0, 10))
        
        self.likes_value = tk.Label(likes_box, text="--", 
            font=("Segoe UI", 16, "bold"), bg="#1a1a1a", fg="white", anchor="w")
        self.likes_value.pack(anchor="w")
        
        self.likes_label = tk.Label(likes_box, text="👍 Likes", 
            font=("Segoe UI", 9), bg="#1a1a1a", fg="#9ca3af", anchor="w")
        self.likes_label.pack(anchor="w")
        
        # Comments
        comments_box = tk.Frame(stats_inner, bg="#1a1a1a")
        comments_box.pack(fill="x")
        
        self.comments_value = tk.Label(comments_box, text="--", 
            font=("Segoe UI", 16, "bold"), bg="#1a1a1a", fg="white", anchor="w")
        self.comments_value.pack(anchor="w")
        
        self.comments_label = tk.Label(comments_box, text="💬 Comments", 
            font=("Segoe UI", 9), bg="#1a1a1a", fg="#9ca3af", anchor="w")
        self.comments_label.pack(anchor="w")

    def set_download_type(self, dtype):
        self.download_type.set(dtype)
        if dtype == "video":
            self.video_btn.configure(bg="#3b82f6", fg="white")
            self.audio_btn.configure(bg="#262626" if self.dark_mode else "#f3f4f6", 
                                    fg="#9ca3af" if self.dark_mode else "#6b7280")
        else:
            self.audio_btn.configure(bg="#3b82f6", fg="white")
            self.video_btn.configure(bg="#262626" if self.dark_mode else "#f3f4f6", 
                                    fg="#9ca3af" if self.dark_mode else "#6b7280")

    def set_thumbnail(self, url=None):
        if not url:
            self.thumbnail_label.config(image="", text="No thumbnail", fg="#6b7280")
            return

        try:
            with urllib.request.urlopen(url) as u:
                raw_data = u.read()

            image = Image.open(io.BytesIO(raw_data))
            image = image.resize((360, 202), Image.LANCZOS)

            self.thumbnail_img = ImageTk.PhotoImage(image)
            self.thumbnail_label.config(image=self.thumbnail_img, text="")

        except Exception:
            self.thumbnail_label.config(image="", text="Failed to load thumbnail", fg="#6b7280")

    def log_status(self, msg):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, msg + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")

    def progress_hook(self, d):
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "0%").replace("%", "").strip()
            speed = d.get("_speed_str", "--")
            eta = d.get("_eta_str", "--")

            try:
                percent_float = float(percent)
            except ValueError:
                percent_float = 0.0

            self.root.after(0, self.update_progress, percent_float, speed, eta)

        elif d["status"] == "finished":
            self.root.after(0, self.update_progress, 100, "Complete", "0s")

    def update_progress(self, percent, speed, eta):
        self.progress_var.set(percent)
        width = self.progress_canvas.winfo_width()
        fill_width = max(1, (width * percent) / 100)
        self.progress_canvas.coords(self.progress_fill, 0, 0, fill_width, 8)
        self.progress_percent.config(text=f"{percent:.1f}%")
        self.progress_speed.config(text=f"⚡ {speed}")
        self.progress_eta.config(text=f"⏱️ {eta}")

    def reset_progress(self):
        self.update_progress(0, "--", "--")

    def fetch_info(self):
        url = self.url_entry.get().strip()
        if not url or url == "https://www.youtube.com/watch?v=...":
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return

        self.fetch_btn.config(state="disabled")
        self.log_status("🔍 Fetching video information...")
        threading.Thread(target=self._fetch_info_thread, args=(url,), daemon=True).start()

    def _fetch_info_thread(self, url):
        try:
            with yt_dlp.YoutubeDL({"quiet": True, "skip_download": True}) as ydl:
                info = ydl.extract_info(url, download=False)

            self.video_info = info
            
            self.root.after(0, self.video_title.config, {"text": info.get('title', 'Unknown')})
            self.root.after(0, self.video_channel.config, {"text": f"📺 {info.get('uploader', 'Unknown')}"})
            self.root.after(0, self.video_duration.config, {"text": f"⏱️ Duration: {format_duration(info.get('duration'))}"})
            
            self.root.after(0, self.views_value.config, {"text": format_number(info.get('view_count'))})
            self.root.after(0, self.likes_value.config, {"text": format_number(info.get('like_count'))})
            self.root.after(0, self.comments_value.config, {"text": format_number(info.get('comment_count'))})
            
            self.root.after(0, self.set_thumbnail, info.get("thumbnail"))
            self.root.after(0, self.log_status, f"✅ Fetched: {info.get('title')}")

        except Exception as e:
            self.root.after(0, self.log_status, f"❌ Error: {e}")

        finally:
            self.root.after(0, lambda: self.fetch_btn.config(state="normal"))

    def start_download(self):
        url = self.url_entry.get().strip()
        if not url or url == "https://www.youtube.com/watch?v=...":
            messagebox.showerror("Error", "Please enter a valid YouTube URL.")
            return

        self.download_btn.config(state="disabled")
        self.log_status(f"⬇️ Starting download ({self.download_type.get()})...")
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def download_video(self, url):
        try:
            self.root.after(0, self.reset_progress)

            ydl_opts = {
                "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
                "progress_hooks": [self.progress_hook],
                "quiet": True,
            }

            if self.download_type.get() == "audio":
                ydl_opts.update({
                    "format": "bestaudio/best",
                    "writethumbnail": True,
                    "postprocessors": [
                        {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"},
                        {"key": "EmbedThumbnail"},
                        {"key": "FFmpegMetadata"},
                    ],
                })
            else:
                ydl_opts.update({
                    "format": "bestvideo+bestaudio/best",
                    "merge_output_format": "mp4",
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                self.root.after(0, self.log_status, f"✅ Downloaded: {info.get('title')}")
                
                # Keep info displayed after download
                if not self.video_info:
                    self.video_info = info
                    self.root.after(0, self.video_title.config, {"text": info.get('title', 'Unknown')})
                    self.root.after(0, self.video_channel.config, {"text": f"📺 {info.get('uploader', 'Unknown')}"})
                    self.root.after(0, self.video_duration.config, {"text": f"⏱️ Duration: {format_duration(info.get('duration'))}"})
                    self.root.after(0, self.views_value.config, {"text": format_number(info.get('view_count'))})
                    self.root.after(0, self.likes_value.config, {"text": format_number(info.get('like_count'))})
                    self.root.after(0, self.comments_value.config, {"text": format_number(info.get('comment_count'))})
                    self.root.after(0, self.set_thumbnail, info.get("thumbnail"))

        except Exception as e:
            self.root.after(0, self.log_status, f"❌ Error: {e}")

        finally:
            self.root.after(0, lambda: self.download_btn.config(state="normal"))


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop() 