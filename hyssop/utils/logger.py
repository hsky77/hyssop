import logging
from multiprocessing import Queue

LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s - %(message)s"


class MultiProcessingQueueHandle(logging.Handler):
    def __init__(self, log_queue: Queue) -> None:
        super().__init__()
        self.process_queue = log_queue

    def emit(self, record):
        if self.process_queue is not None:
            self.process_queue.put_nowait(record.getMessage())


logging.basicConfig(format=LOG_FORMAT)
