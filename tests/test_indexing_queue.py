import unittest
import time
import threading
from core.indexing.queue_manager import IndexingQueueManager, QueueItem

class TestIndexingQueue(unittest.TestCase):
    def test_priority(self):
        qm = IndexingQueueManager()
        qm.add_task("file1.txt", "update")
        qm.add_task("file2.txt", "deleted")
        
        # Expect deleted (priority 0) before update (priority 10)
        item1 = qm.get_next_task()
        self.assertEqual(item1.path, "file2.txt")
        self.assertEqual(item1.status, "deleted")
        
        item2 = qm.get_next_task()
        self.assertEqual(item2.path, "file1.txt")
        self.assertEqual(item2.status, "update")

    def test_deduplication_update_update(self):
        qm = IndexingQueueManager()
        qm.add_task("file1.txt", "update")
        time.sleep(0.1)
        qm.add_task("file1.txt", "update") 
        
        # Should only get one task (the latest one)
        # Note: In implementation, we might get multiple pops but invalid ones are skipped
        # let's verify get_next_task returns only one valid item
        
        item = qm.get_next_task()
        self.assertIsNotNone(item)
        self.assertEqual(item.path, "file1.txt")
        
        item2 = qm.get_next_task()
        self.assertIsNone(item2)

    def test_deduplication_delete_override(self):
        qm = IndexingQueueManager()
        # file1 updated then deleted
        qm.add_task("file1.txt", "update")
        qm.add_task("file1.txt", "deleted")
        
        item = qm.get_next_task()
        self.assertEqual(item.path, "file1.txt")
        self.assertEqual(item.status, "deleted")
        
        item2 = qm.get_next_task()
        self.assertIsNone(item2)

if __name__ == '__main__':
    unittest.main()
