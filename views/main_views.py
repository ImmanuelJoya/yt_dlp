import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import urllib.request
import io

from utils.formatters import format_duration, format_number


class MainView:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader")
        self.root.geometry("1100x750")
        self.root.resizable(False, False)

        self.controller = None
        self.thumbnail_img = None
        self._build_ui()
        self._apply_modern_theme()
        self._bind_accessibility()

    # =========================
    # Controller Binding
    # =========================
    def set_controller(self, controller):
        self.controller = controller

    # =========================
    # UI Construction
    # =========================
    def _build_ui(self):
        # Main container
        self.main = tk.Frame(self.root, bg="#0a0a0a")
        self.main.pack(fill="both", expand=True, padx=30, pady=30)

        # Header
        header = tk.Frame(self.main, bg="#0a0a0a")
        header.pack(fill="x", pady=(0, 30))

        title = tk.Label(
            header,
            text="YouTube Downloader",
            font=("Segoe UI", 32, "bold"),
            bg="#0a0a0a",
            fg="#ffffff"
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header,
            text="Download videos and audio in high quality",
            font=("Segoe UI", 11),
            bg="#0a0a0a",
            fg="#a0a0a0"
        )
        subtitle.pack(anchor="w")

        # Content
        content = tk.Frame(self.main, bg="#0a0a0a")
        content.pack(fill="both", expand=True)

        # Left Panel
        self.left = tk.Frame(content, bg="#0a0a0a")
        self.left.pack(side="left", fill="both", expand=True, padx=(0, 25))

        # Right Panel
        self.right = tk.Frame(content, bg="#1a1a1a", width=380)
        self.right.pack(side="right", fill="y", padx=0, pady=0)
        self.right.pack_propagate(False)

        self._build_left_panel()
        self._build_right_panel()

    # =========================
    # Left Panel
    # =========================
    def _build_left_panel(self):
        # URL
        url_label = tk.Label(
            self.left, 
            text="YouTube URL", 
            font=("Segoe UI", 11, "bold"),
            bg="#0a0a0a",
            fg="#ffffff"
        )
        url_label.pack(anchor="w", pady=(0, 8))

        self.url_entry = ttk.Entry(
            self.left, 
            font=("Segoe UI", 12),
            style="Modern.TEntry"
        )
        self.url_entry.pack(fill="x", pady=(0, 25), ipady=12)
        self.url_entry.insert(0, "https://www.youtube.com/watch?v= ...")

        # Download Type
        type_frame = tk.Frame(self.left, bg="#0a0a0a")
        type_frame.pack(fill="x", pady=(0, 25))

        self.download_type = tk.StringVar(value="video")
        
        self.video_btn = ttk.Button(
            type_frame, 
            text="🎬 Video",
            style="Type.TButton",
            command=lambda: self._set_type("video")
        )
        self.video_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        self.audio_btn = ttk.Button(
            type_frame, 
            text="🎵 Audio",
            style="Type.TButton",
            command=lambda: self._set_type("audio")
        )
        self.audio_btn.pack(side="left", expand=True, fill="x")

        # Quality
        quality_label = tk.Label(
            self.left, 
            text="Quality", 
            font=("Segoe UI", 10),
            bg="#0a0a0a",
            fg="#a0a0a0"
        )
        quality_label.pack(anchor="w", pady=(0, 8))

        self.quality = tk.StringVar(value="1080p")
        quality_menu = ttk.OptionMenu(
            self.left,
            self.quality,
            "1080p",
            "720p", "1080p", "4K",
            style="Modern.TMenubutton"
        )
        quality_menu.pack(anchor="w", pady=(0, 25))

        # Buttons
        btn_frame = tk.Frame(self.left, bg="#0a0a0a")
        btn_frame.pack(fill="x", pady=(0, 25))

        self.fetch_btn = ttk.Button(
            btn_frame, 
            text="📥 Fetch Info",
            style="Action.TButton",
            command=self._on_fetch
        )
        self.fetch_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))

        self.download_btn = ttk.Button(
            btn_frame, 
            text="⬇️ Download",
            style="Action.TButton",
            command=self._on_download
        )
        self.download_btn.pack(side="left", expand=True, fill="x")

        # Progress
        self.progress_bar = ttk.Progressbar(
            self.left,
            style="Modern.Horizontal.TProgressbar",
            mode="determinate",
            maximum=100,
            value=0
        )
        self.progress_bar.pack(fill="x", pady=(0, 5))

        self.progress_label = tk.Label(
            self.left, 
            text="0%",
            font=("Segoe UI", 9),
            bg="#0a0a0a",
            fg="#a0a0a0"
        )
        self.progress_label.pack(anchor="w", pady=(0, 20))

        # Status
        status_container = tk.Frame(self.left, bg="#1a1a1a")
        status_container.pack(fill="both", expand=True)

        self.status = tk.Text(
            status_container, 
            height=8, 
            state="disabled", 
            font=("Consolas", 9),
            bg="#1a1a1a",
            fg="#e0e0e0",
            bd=0,
            highlightthickness=0,
            relief="flat"
        )
        self.status.pack(fill="both", expand=True, padx=15, pady=15)

    # =========================
    # Right Panel
    # =========================
    def _build_right_panel(self):
        right_container = tk.Frame(self.right, bg="#1a1a1a")
        right_container.pack(fill="both", expand=True, padx=20, pady=20)

        self.thumb_label = tk.Label(
            right_container, 
            text="No thumbnail",
            bg="#1a1a1a",
            fg="#606060"
        )
        self.thumb_label.pack(fill="x", pady=(0, 20))

        self.title_label = tk.Label(
            right_container,
            text="No video loaded",
            font=("Segoe UI", 12, "bold"),
            wraplength=340,
            justify="left",
            bg="#1a1a1a",
            fg="#ffffff"
        )
        self.title_label.pack(anchor="w", pady=(0, 8))

        self.channel_label = tk.Label(
            right_container, 
            text="Unknown channel",
            font=("Segoe UI", 10),
            bg="#1a1a1a",
            fg="#a0a0a0"
        )
        self.channel_label.pack(anchor="w", pady=(0, 5))

        self.duration_label = tk.Label(
            right_container, 
            text="Duration: --:--",
            font=("Segoe UI", 10),
            bg="#1a1a1a",
            fg="#a0a0a0"
        )
        self.duration_label.pack(anchor="w", pady=(0, 15))

        self.views_label = tk.Label(
            right_container, 
            text="👁️ --",
            font=("Segoe UI", 10),
            bg="#1a1a1a",
            fg="#a0a0a0"
        )
        self.views_label.pack(anchor="w", pady=(0, 5))

        self.likes_label = tk.Label(
            right_container, 
            text="👍 --",
            font=("Segoe UI", 10),
            bg="#1a1a1a",
            fg="#a0a0a0"
        )
        self.likes_label.pack(anchor="w", pady=(0, 5))

        self.comments_label = tk.Label(
            right_container, 
            text="💬 --",
            font=("Segoe UI", 10),
            bg="#1a1a1a",
            fg="#a0a0a0"
        )
        self.comments_label.pack(anchor="w")

    # =========================
    # Actions
    # =========================
    def _on_fetch(self):
        url = self.url_entry.get().strip()
        if not self.controller:
            return
        self.fetch_btn.config(state="disabled")
        self.log_status("🔍 Fetching info...")
        self.controller.fetch_info(url)

    def _on_download(self):
        url = self.url_entry.get().strip()
        if not self.controller:
            return

        self.download_btn.config(state="disabled")
        self.log_status("⬇️ Starting download...")

        if self.download_type.get() == "audio":
            opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {"key": "FFmpegExtractAudio", "preferredcodec": "mp3"},
                    {"key": "FFmpegMetadata"},
                    {"key": "EmbedThumbnail"},
                ],
            }
        else:
            quality_map = {
                "720p": "bestvideo[height<=720]+bestaudio/best",
                "1080p": "bestvideo[height<=1080]+bestaudio/best",
                "4K": "bestvideo[height<=2160]+bestaudio/best",
            }
            opts = {
                "format": quality_map[self.quality.get()],
                "merge_output_format": "mp4",
            }

        self.controller.download(url, opts)

    # =========================
    # UI Updates (Called by Controller)
    # =========================
    def update_video_info(self, info):
        self.title_label.config(text=info.get("title", "Unknown"))
        self.channel_label.config(text=f"📺 {info.get('uploader', 'Unknown')}")
        self.duration_label.config(
            text=f"⏱️ {format_duration(info.get('duration'))}"
        )
        self.views_label.config(text=f"👁️ {format_number(info.get('view_count'))}")
        self.likes_label.config(text=f"👍 {format_number(info.get('like_count'))}")
        self.comments_label.config(text=f"💬 {format_number(info.get('comment_count'))}")

        self._set_thumbnail(info.get("thumbnail"))

    def _set_thumbnail(self, url):
        if not url:
            self.thumb_label.config(text="No thumbnail", image="")
            return
        try:
            data = urllib.request.urlopen(url).read()
            img = Image.open(io.BytesIO(data)).resize((340, 191))
            self.thumbnail_img = ImageTk.PhotoImage(img)
            self.thumb_label.config(image=self.thumbnail_img, text="")
        except Exception:
            self.thumb_label.config(text="Thumbnail error", image="")

    def progress_hook(self, d):
        if d["status"] == "downloading":
            percent = float(d.get("_percent_str", "0%").replace("%", "").strip())
            self.root.after(0, self._update_progress, percent)

        elif d["status"] == "finished":
            self.root.after(0, self._update_progress, 100)

    def _update_progress(self, percent):
        self.progress_bar["value"] = percent
        self.progress_label.config(text=f"{percent:.1f}%")

    def reset_progress(self):
        self.progress_bar["value"] = 0
        self.progress_label.config(text="0%")

    def log_status(self, msg):
        self.status.config(state="normal")
        self.status.insert("end", msg + "\n")
        self.status.see("end")
        self.status.config(state="disabled")

    def enable_fetch(self):
        self.fetch_btn.config(state="enabled")

    def enable_download(self):
        self.download_btn.config(state="enabled")

    # =========================
    # Theme & Styling
    # =========================
    def _apply_modern_theme(self):
        style = ttk.Style()
        
        # Base colors
        bg_dark = "#0a0a0a"
        bg_medium = "#1a1a1a"
        bg_light = "#2d2d2d"
        text_primary = "#ffffff"
        text_secondary = "#a0a0a0"
        accent = "#3a86ff"
        accent_hover = "#5a9cff"
        border = "#404040"
        
        # Update root
        self.root.configure(bg=bg_dark)
        
        # Configure ttk styles
        style.theme_use("clam")
        
        # Entry style
        style.configure(
            "Modern.TEntry",
            fieldbackground=bg_medium,
            foreground=text_primary,
            bordercolor=border,
            lightcolor=bg_medium,
            darkcolor=bg_medium,
            insertcolor=text_primary,
            padding=10
        )
        
        # Button styles
        style.configure(
            "Type.TButton",
            background=bg_medium,
            foreground=text_primary,
            bordercolor=border,
            lightcolor=bg_medium,
            darkcolor=bg_medium,
            padding=15,
            font=("Segoe UI", 11)
        )
        style.map(
            "Type.TButton",
            background=[("active", bg_light), ("pressed", bg_dark)],
            foreground=[("active", text_primary), ("pressed", text_primary)],
            relief=[("pressed", "flat")]
        )
        
        style.configure(
            "Action.TButton",
            background=accent,
            foreground=bg_dark,
            bordercolor=accent,
            lightcolor=accent,
            darkcolor=accent,
            padding=15,
            font=("Segoe UI", 11, "bold")
        )
        style.map(
            "Action.TButton",
            background=[("active", accent_hover), ("pressed", accent)],
            foreground=[("active", bg_dark), ("pressed", bg_dark)]
        )
        
        # Menubutton style
        style.configure(
            "Modern.TMenubutton",
            background=bg_medium,
            foreground=text_primary,
            bordercolor=border,
            arrowcolor=text_primary,
            padding=10,
            font=("Segoe UI", 10)
        )
        style.map(
            "Modern.TMenubutton",
            background=[("active", bg_light)]
        )
        
        # Progressbar style
        style.configure(
            "Modern.Horizontal.TProgressbar",
            background=accent,
            troughcolor=bg_medium,
            thickness=6,
            bordercolor=bg_dark,
            lightcolor=accent,
            darkcolor=accent
        )

    # =========================
    # Helpers
    # =========================
    def _set_type(self, t):
        self.download_type.set(t)
        active_style = "Type.TButton"
        # Update active state visuals
        if t == "video":
            self.video_btn.config(style="Action.TButton")
            self.audio_btn.config(style="Type.TButton")
        else:
            self.audio_btn.config(style="Action.TButton")
            self.video_btn.config(style="Type.TButton")

    def _bind_accessibility(self):
        self.root.bind("<Return>", lambda e: self.fetch_btn.invoke())
        self.root.bind("<Control-d>", lambda e: self.download_btn.invoke())
        self.url_entry.focus_set()