import collections
import threading
import logging

"""
You might use Python’s built-in queue.Queue, which is thread-safe out-of-the-box. 
However, deque gives you more control if you later decide to persist to disk.
"""

class RetryQueue:
    """
    A simple in-memory retry queue that holds items for later reprocessing.
    """
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.queue = collections.deque()
        self.lock = threading.Lock()

    def enqueue(self, item):
        with self.lock:
            self.queue.append(item)
            self.logger.debug("Enqueued snapshot for retry. Queue size=%d", len(self.queue))

    def dequeue_all(self):
        """
        Returns all items in the queue and clears it.
        """
        with self.lock:
            items = list(self.queue)
            self.queue.clear()
            return items

    def size(self):
        with self.lock:
            return len(self.queue)
