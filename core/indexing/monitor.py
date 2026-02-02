from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

class IndexingHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback # 변경 발생 시 알림 받을 콜백

    def on_modified(self, event):
        if not event.is_directory:
            if self.callback: self.callback(event.src_path, "modified")

    def on_created(self, event):
        if not event.is_directory:
            if self.callback: self.callback(event.src_path, "created")

    def on_deleted(self, event):
        if not event.is_directory:
            if self.callback: self.callback(event.src_path, "deleted")

class FileMonitor:
    def __init__(self):
        self.observer = Observer()
        self.watch_list = {}

    def add_path(self, path, callback=None):
        if path not in self.watch_list:
            handler = IndexingHandler(callback)
            watch = self.observer.schedule(handler, path, recursive=True)
            self.watch_list[path] = watch
            print(f"Started monitoring: {path}")

    def remove_path(self, path):
        if path in self.watch_list:
            self.observer.unschedule(self.watch_list[path])
            del self.watch_list[path]
            print(f"Stopped monitoring: {path}")

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()
