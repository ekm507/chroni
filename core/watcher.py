# core/watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from core.scanner import Scanner

class ChroniEventHandler(FileSystemEventHandler):
    def on_modified(self, event):
        scanner = Scanner()
        if not event.is_directory:
            scanner.handle_file_change(event.src_path)

    def on_created(self, event):
        scanner = Scanner()
        if not event.is_directory:
            scanner.handle_file_change(event.src_path)

    def on_deleted(self, event):
        scanner = Scanner()
        if not event.is_directory:
            scanner.handle_file_change(event.src_path)

def start_watching(tracked_paths):
    observer = Observer()
    handler = ChroniEventHandler()
    for path in tracked_paths:
        observer.schedule(handler, path=path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
