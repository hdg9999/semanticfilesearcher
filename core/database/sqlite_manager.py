import sqlite3
import os
from datetime import datetime
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path="data/metadata.db"):
        if os.path.dirname(db_path):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    extension TEXT,
                    last_modified TIMESTAMP,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # FileTags relationship table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_tags (
                    file_id INTEGER,
                    tag_id INTEGER,
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE,
                    FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE,
                    PRIMARY KEY(file_id, tag_id)
                )
            """)
            conn.commit()

    def upsert_file(self, file_path, last_modified):
        file_name = os.path.basename(file_path)
        extension = os.path.splitext(file_path)[1].lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO files (file_path, file_name, extension, last_modified)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(file_path) DO UPDATE SET
                    last_modified=excluded.last_modified,
                    indexed_at=CURRENT_TIMESTAMP
            """, (file_path, file_name, extension, last_modified))
            conn.commit()
            return cursor.lastrowid

    def add_tag(self, tag_name):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
            conn.commit()
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            return cursor.fetchone()[0]

    def link_file_tag(self, file_path, tag_name):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM files WHERE file_path = ?", (file_path,))
            file_row = cursor.fetchone()
            if not file_row: return
            
            tag_id = self.add_tag(tag_name)
            cursor.execute("INSERT OR IGNORE INTO file_tags (file_id, tag_id) VALUES (?, ?)", 
                           (file_row[0], tag_id))
            conn.commit()

    def get_all_tags(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM tags")
            return [row[0] for row in cursor.fetchall()]

    def search_by_tag(self, tag_name):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT f.file_path FROM files f
                JOIN file_tags ft ON f.id = ft.file_id
                JOIN tags t ON ft.tag_id = t.id
                WHERE t.name = ?
            """, (tag_name,))
            return [row[0] for row in cursor.fetchall()]

    def get_tags_for_file(self, file_path):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.name FROM tags t
                JOIN file_tags ft ON t.id = ft.tag_id
                JOIN files f ON f.id = ft.file_id
                WHERE f.file_path = ?
            """, (file_path,))
            return [row[0] for row in cursor.fetchall()]

    def delete_tag(self, tag_name):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tags WHERE name = ?", (tag_name,))
            conn.commit()

    def rename_tag(self, old_name, new_name):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE tags SET name = ? WHERE name = ?", (new_name, old_name))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False

    def update_file_tags(self, file_path, new_tags):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. Get file ID
            cursor.execute("SELECT id FROM files WHERE file_path = ?", (file_path,))
            file_row = cursor.fetchone()
            if not file_row: return
            file_id = file_row[0]

            # 2. Get tag IDs for new tags (create if not exists)
            tag_ids = []
            for tag in new_tags:
                cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag,))
                cursor.execute("SELECT id FROM tags WHERE name = ?", (tag,))
                tag_ids.append(cursor.fetchone()[0])
            
            # 3. Update relationships
            # Remove old
            cursor.execute("DELETE FROM file_tags WHERE file_id = ?", (file_id,))
            # Add new
            for tag_id in tag_ids:
                cursor.execute("INSERT INTO file_tags (file_id, tag_id) VALUES (?, ?)", (file_id, tag_id))
            conn.commit()

    def delete_file(self, file_path):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM files WHERE file_path = ?", (file_path,))
            conn.commit()

    def get_file_metadata(self, file_path):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT last_modified FROM files WHERE file_path = ?", (file_path,))
            row = cursor.fetchone()
            if row:
                return {"last_modified": row[0]}
            return None
