import unittest
import os
import sqlite3
from core.database.sqlite_manager import DatabaseManager

class TestTagManager(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_metadata.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = DatabaseManager(self.test_db)

    def tearDown(self):
        if os.path.exists(self.test_db):
            try:
                os.remove(self.test_db)
            except PermissionError:
                pass # Might be locked

    def test_add_and_get_tags(self):
        self.db.add_tag("TestTag1")
        self.db.add_tag("TestTag2")
        tags = self.db.get_all_tags()
        self.assertIn("TestTag1", tags)
        self.assertIn("TestTag2", tags)
        self.assertEqual(len(tags), 2)

    def test_link_file_tag(self):
        file_path = "C:/test/file1.txt"
        self.db.upsert_file(file_path, "2024-01-01 00:00:00")
        
        self.db.link_file_tag(file_path, "TagA")
        tags = self.db.get_tags_for_file(file_path)
        self.assertEqual(tags, ["TagA"])
        
        # Add another
        self.db.link_file_tag(file_path, "TagB")
        tags = self.db.get_tags_for_file(file_path)
        self.assertIn("TagA", tags)
        self.assertIn("TagB", tags)

    def test_update_file_tags(self):
        file_path = "C:/test/file2.txt"
        self.db.upsert_file(file_path, "2024-01-01 00:00:00")
        
        # Initial
        self.db.link_file_tag(file_path, "Initial")
        
        # Update (Replace)
        self.db.update_file_tags(file_path, ["New1", "New2"])
        tags = self.db.get_tags_for_file(file_path)
        self.assertEqual(set(tags), {"New1", "New2"})
        self.assertNotIn("Initial", tags)

    def test_delete_tag(self):
        self.db.add_tag("DeleteMe")
        self.db.add_tag("KeepMe")
        
        self.db.delete_tag("DeleteMe")
        
        tags = self.db.get_all_tags()
        self.assertNotIn("DeleteMe", tags)
        self.assertIn("KeepMe", tags)

    def test_rename_tag(self):
        self.db.add_tag("OldName")
        success = self.db.rename_tag("OldName", "NewName")
        
        self.assertTrue(success)
        tags = self.db.get_all_tags()
        self.assertIn("NewName", tags)
        self.assertNotIn("OldName", tags)

if __name__ == '__main__':
    unittest.main()
