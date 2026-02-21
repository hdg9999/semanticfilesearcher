import heapq
import time
import threading
from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass(order=True)
class QueueItem:
    priority: int
    timestamp: float
    path: str = field(compare=False)
    status: str = field(compare=False) # "update" or "delete"

    def __init__(self, path: str, status: str):
        self.path = path
        self.status = status
        self.timestamp = time.time()
        # Priority: delete (0) > update (10). Lower number is higher priority in heapq
        if status == "deleted":
            self.priority = 0
        else:
            self.priority = 10

class IndexingQueueManager:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()
        self.pending_tasks: Dict[str, QueueItem] = {} # Deduplication map: path -> QueueItem
        self.current_task: Optional[QueueItem] = None # Currently processing task

    def set_current_task(self, task: QueueItem):
        with self.lock:
            self.current_task = task

    def clear_current_task(self):
        with self.lock:
            self.current_task = None
            
    def get_current_task(self):
        with self.lock:
            return self.current_task

    def add_task(self, path: str, status: str):
        import os
        with self.lock:
            # Check for existing task for this file
            if path in self.pending_tasks:
                existing_item = self.pending_tasks[path]
                
                # Case: Existing update, New delete -> Replace with delete
                if existing_item.status != "deleted" and status == "deleted":
                    # Mark existing as invalid/removed (heapq doesn't support direct removal easily)
                    # We'll just update the map and push the new one. 
                    # When popping, we check if the item is still in pending_tasks and matches.
                    pass 
                
                # Case: Existing delete, New update -> If file exists, update takes precedence (recreation)
                elif existing_item.status == "deleted" and status != "deleted":
                    if not os.path.exists(path):
                        return

                # Case: Same status -> Update timestamp (re-push will happen, old one becomes stale)
            
            item = QueueItem(path, status)
            heapq.heappush(self.queue, item)
            self.pending_tasks[path] = item
            print(f"[Queue] Added task: {status} {path} (Queue size: {len(self.queue)})")

    def get_next_task(self) -> Optional[QueueItem]:
        with self.lock:
            while self.queue:
                item = heapq.heappop(self.queue)
                
                # Validate if this item is the latest for this path
                if item.path in self.pending_tasks and self.pending_tasks[item.path] == item:
                    del self.pending_tasks[item.path]
                    return item
                else:
                    # This item is stale (superceeded by a newer task for same file)
                    continue
            return None

    def get_queue_size(self):
        with self.lock:
            return len(self.pending_tasks)

    def get_pending_items(self):
        with self.lock:
            return list(self.pending_tasks.values())
