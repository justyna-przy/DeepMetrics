import collections
import threading
import logging
import itertools

class CommandQueue:
    """
    A thread-safe in-memory queue for commands.
    """
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.queue = collections.deque()
        self.lock = threading.Lock()
        self._id_counter = itertools.count(1)  # Incrementing ID generator

    def enqueue(self, cmd: dict) -> int:
        """
        Enqueue a new command (dict) and assign a unique command_id.
        """
        with self.lock:
            command_id = next(self._id_counter)
            cmd["command_id"] = command_id
            self.queue.append(cmd)
            self.logger.info(
                "Enqueued command %s for aggregator '%s' device '%s'",
                command_id, cmd.get("aggregator_name"), cmd.get("device_name")
            )
            return command_id

    def get_unacked_for_aggregator(self, aggregator_name: str):
        """
        Return all commands for a specific aggregator (unacked = still in the queue).
        """
        with self.lock:
            return [cmd for cmd in self.queue if cmd["aggregator_name"] == aggregator_name]

    def ack(self, aggregator_name: str, command_ids: list):
        """
        Acknowledge (remove) commands by ID for a particular aggregator.
        """
        with self.lock:
            old_size = len(self.queue)
            self.queue = collections.deque(
                cmd for cmd in self.queue
                if not (cmd["aggregator_name"] == aggregator_name and cmd["command_id"] in command_ids)
            )
            new_size = len(self.queue)
            self.logger.info(
                "Acked command IDs %s for aggregator '%s'. Queue size: %d -> %d",
                command_ids, aggregator_name, old_size, new_size
            )
