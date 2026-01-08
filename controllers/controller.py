import threading
from models.downloader import YouTubeDownloader


class AppController:
    def __init__(self, view):
        self.view = view
        self.model = YouTubeDownloader(self.view.progress_hook)

    def fetch_info(self, url):
        def task():
            try:
                info = self.model.fetch_info(url)
                self.view.root.after(0, self.view.update_video_info, info)
                self.view.root.after(0, self.view.log_status, "✅ Info fetched")
            except Exception as e:
                self.view.root.after(0, self.view.log_status, f"❌ {e}")
            finally:
                self.view.root.after(0, self.view.enable_fetch)

        threading.Thread(target=task, daemon=True).start()

    def download(self, url, ydl_opts):
        def task():
            try:
                self.view.root.after(0, self.view.reset_progress)
                info = self.model.download(url, ydl_opts)
                self.view.root.after(0, self.view.update_video_info, info)
                self.view.root.after(0, self.view.log_status, "✅ Download complete")
            except Exception as e:
                self.view.root.after(0, self.view.log_status, f"❌ {e}")
            finally:
                self.view.root.after(0, self.view.enable_download)

        threading.Thread(target=task, daemon=True).start()
