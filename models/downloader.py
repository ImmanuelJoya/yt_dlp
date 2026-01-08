import yt_dlp
import os

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


class YouTubeDownloader:
    def __init__(self, progress_hook):
        self.progress_hook = progress_hook

    def fetch_info(self, url):
        with yt_dlp.YoutubeDL({
            "quiet": True,
            "skip_download": True
        }) as ydl:
            return ydl.extract_info(url, download=False)

    def download(self, url, options):
        ydl_opts = {
            "outtmpl": f"{DOWNLOAD_DIR}/%(title).200s.%(ext)s",
            "progress_hooks": [self.progress_hook],
            "quiet": True,
            **options
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=True)
