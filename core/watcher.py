import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from core.scanner import Scanner
from utils.paths import get_tracked_paths_file
from core.tracker import Tracker

class ChroniEventHandler(FileSystemEventHandler):
    def __init__(self, scanner: Scanner):
        self.scanner = scanner

    def on_modified(self, event):
        if not event.is_directory:
            self.scanner.handle_file_change(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.scanner.handle_file_change(event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.scanner.handle_file_change(event.src_path)


class TrackedPathsWatcher(FileSystemEventHandler):
    def __init__(self, observer: Observer, main_handler: ChroniEventHandler):
        self.tracker = Tracker()
        self.observer = observer
        self.main_handler = main_handler
        self.tracked_file = get_tracked_paths_file()
        self.current_paths = set()
        self._init_tracked_paths()

    def _init_tracked_paths(self):
        self.current_paths = set(self.tracker.read_tracked_paths())
        self._schedule_all()

    def _schedule_all(self):
        for path in self.current_paths:
            p = Path(path)
            if p.exists():
                self.observer.schedule(self.main_handler, path=path, recursive=p.is_dir())

    def _unschedule_all(self):
        self.observer.unschedule_all()

    def _reload_tracked_paths(self):
        print("Tracked paths file changed, reloading watcher paths...")
        self._unschedule_all()
        self._init_tracked_paths()

    def on_modified(self, event):
        if Path(event.src_path).resolve() == Path(self.tracked_file):
            self._reload_tracked_paths()


def start_watching():
    observer = Observer()
    scanner = Scanner()
    main_handler = ChroniEventHandler(scanner)
    paths_handler = TrackedPathsWatcher(observer, main_handler)

    # Watch the tracked paths list file
    observer.schedule(paths_handler, path=str(get_tracked_paths_file()), recursive=False)

    observer.start()
    print("Chroni watcher started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping Chroni watcher...")
        observer.stop()
    observer.join()
