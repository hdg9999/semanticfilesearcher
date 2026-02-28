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
                    color TEXT DEFAULT '#007acc',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Migration: Add color column if not exists
            cursor.execute("PRAGMA table_info(tags)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'color' not in columns:
                cursor.execute("ALTER TABLE tags ADD COLUMN color TEXT DEFAULT '#007acc'")
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

            # FileVectors table (Vector DB ID mapping)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS file_vectors (
                    id INTEGER PRIMARY KEY, -- This will be the Vector DB ID
                    file_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(file_id) REFERENCES files(id) ON DELETE CASCADE
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
            
            # lastrowid는 Insert/Update 상태에 따라 값이 다를 수 있으므로 명시적으로 ID 조회
            cursor.execute("SELECT id FROM files WHERE file_path = ?", (file_path,))
            return cursor.fetchone()[0]

    def add_tag(self, tag_name, color="#007acc"):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO tags (name, color) VALUES (?, ?)", (tag_name, color))
            conn.commit()
            cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
            return cursor.fetchone()[0]

    def update_tag_color(self, tag_name, color):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE tags SET color = ? WHERE name = ?", (color, tag_name))
            conn.commit()
            return cursor.rowcount > 0

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
            cursor.execute("SELECT name, color FROM tags")
            return cursor.fetchall() # Returns list of (name, color) tuples

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

    def search_by_tags(self, tags, condition="AND"):
        if not tags: return []
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if condition == "OR":
                placeholders = ",".join(["?"] * len(tags))
                query = f"""
                    SELECT DISTINCT f.file_path FROM files f
                    JOIN file_tags ft ON f.id = ft.file_id
                    JOIN tags t ON ft.tag_id = t.id
                    WHERE t.name IN ({placeholders})
                """
                cursor.execute(query, tags)
                
            else: # AND
                # Find files that have ALL tags
                # Use intersection or count grouping
                placeholders = ",".join(["?"] * len(tags))
                query = f"""
                    SELECT f.file_path FROM files f
                    JOIN file_tags ft ON f.id = ft.file_id
                    JOIN tags t ON ft.tag_id = t.id
                    WHERE t.name IN ({placeholders})
                    GROUP BY f.id
                    HAVING COUNT(DISTINCT t.id) = ?
                """
                cursor.execute(query, tags + [len(tags)])
                
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

    def get_tags_for_files(self, file_paths):
        """
        Retrieves tags for a list of files efficiently.
        Returns: Dict[str, List[Tuple[str, str]]] -> {file_path: [(tag_name, tag_color), ...]}
        """
        if not file_paths:
            return {}

        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(file_paths))
            query = f"""
                SELECT f.file_path, t.name, t.color 
                FROM files f
                JOIN file_tags ft ON f.id = ft.file_id
                JOIN tags t ON ft.tag_id = t.id
                WHERE f.file_path IN ({placeholders})
            """
            cursor.execute(query, file_paths)
            
            result = {}
            for row in cursor.fetchall():
                path, tag_name, tag_color = row
                if path not in result:
                    result[path] = []
                result[path].append((tag_name, tag_color))
            return result

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
            
            # If file doesn't exist in DB, try to insert it first
            if not file_row:
                 if os.path.exists(file_path):
                     try:
                         # Simple insertion to ensure file exists in DB
                         file_name = os.path.basename(file_path)
                         extension = os.path.splitext(file_path)[1].lower()
                         mtime = os.path.getmtime(file_path)
                         
                         cursor.execute("""
                            INSERT INTO files (file_path, file_name, extension, last_modified)
                            VALUES (?, ?, ?, ?)
                         """, (file_path, file_name, extension, mtime))
                         file_id = cursor.lastrowid
                     except Exception as e:
                         print(f"Error auto-registering file {file_path}: {e}")
                         return
                 else:
                     return # File not found on disk
            else:
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

    def allocate_vector_id(self, file_id):
        """Allocates a new Vector ID for the given file."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO file_vectors (file_id) VALUES (?)", (file_id,))
            conn.commit()
            return cursor.lastrowid

    def get_vector_ids(self, file_id):
        """Retrieves all vector IDs associated with a file."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM file_vectors WHERE file_id = ?", (file_id,))
            return [row[0] for row in cursor.fetchall()]

    def delete_vector_ids(self, vector_ids):
        """Deletes specific vector IDs from the mapping table."""
        if not vector_ids:
            return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(vector_ids))
            cursor.execute(f"DELETE FROM file_vectors WHERE id IN ({placeholders})", vector_ids)
            conn.commit()

    def get_file_paths_by_vector_ids(self, vector_ids):
        """Retrieves file paths for a given list of vector IDs.
        Returns a dict: {vector_id: file_path}
        """
        if not vector_ids:
            return {}
            
        with self._get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(vector_ids))
            query = f"""
                SELECT fv.id, f.file_path 
                FROM file_vectors fv
                JOIN files f ON fv.file_id = f.id
                WHERE fv.id IN ({placeholders})
            """
            cursor.execute(query, vector_ids)
            
            result = {}
            for row in cursor.fetchall():
                result[row[0]] = row[1]
            return result

    def get_file_id(self, file_path):
        """Retrieves file ID for a given path."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM files WHERE file_path = ?", (file_path,))
            row = cursor.fetchone()
            return row[0] if row else None
