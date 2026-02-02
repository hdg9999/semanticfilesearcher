import unittest
from unittest.mock import MagicMock, patch
from core.indexer import SemanticIndexer

class TestIndexerAsync(unittest.TestCase):
    @patch('core.indexer.SemanticIndexer._init_tagger')
    @patch('core.indexer.FileScanner')
    @patch('core.indexer.DatabaseManager')
    @patch('core.indexer.VectorDBManager')
    @patch('core.indexer.QwenEmbeddingAdapter')
    def test_index_folder_async(self, MockEmbed, MockVec, MockDB, MockScanner, MockInitTagger):
        indexer = SemanticIndexer()
        # Mock Queue Manager
        indexer.queue_manager = MagicMock()
        
        # Test index_folder
        with patch('os.walk') as mock_walk:
            mock_walk.return_value = [
                ('/root', [], ['file1.txt', 'file2.txt'])
            ]
            
            indexer.index_folder('/root')
            
            # Since it runs in a thread, we might need to wait a tiny bit or mock threading
            # For simplicity, we can inspect if threading.Thread was called or relies on eventual consistency.
            # But creating a real thread in test is fine.
            import time
            time.sleep(0.1)
            
            # Check if tasks were added
            self.assertEqual(indexer.queue_manager.add_task.call_count, 2)
            indexer.queue_manager.add_task.assert_any_call('/root\\file1.txt', 'update')

if __name__ == '__main__':
    unittest.main()
