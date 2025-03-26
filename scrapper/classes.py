import time
import threading

class AutoCleanDict(dict):
    def __init__(self, *args, timeout=180, cleanup_interval=60, **kwargs):
        self.timeout = timeout
        self.cleanup_interval = cleanup_interval
        self.timestamps = {}
        self.lock = threading.Lock()
        super().__init__(*args, **kwargs)
        self.cleanup_thread = threading.Thread(target=self.cleanup)
        self.cleanup_thread.daemon = True  # Daemonize thread
        self.cleanup_thread.start()

    def __setitem__(self, key, value):
        with self.lock:
            super().__setitem__(key, value)
            self.timestamps[key] = time.time()

    def __delitem__(self, key):
        with self.lock:
            if key in self:
                super().__delitem__(key)
                del self.timestamps[key]

    def cleanup(self):
        while True:
            time.sleep(self.cleanup_interval)
            with self.lock:
                current_time = time.time()
                keys_to_delete = [key for key, timestamp in self.timestamps.items()
                                  if current_time - timestamp > self.timeout]
                for key in keys_to_delete:
                    if key in self:
                        super().__delitem__(key)
                        del self.timestamps[key]