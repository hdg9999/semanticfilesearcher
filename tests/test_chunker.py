import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__main__.__file__))) if '__main__' in globals() else os.getcwd())

from core.indexing.chunker import TextChunker

def test_chunker():
    text = "A" * 1600
    chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
    chunks = chunker.split_text(text)
    
    print(f"Total chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1} length: {len(chunk)}")
        
    assert len(chunks) == 2, "Should split into two chunks"
    assert len(chunks[0]) == 1000, "First chunk should be 1000"
    assert len(chunks[1]) == 800, "Second chunk should be remainder + overlap, wait 1600-1000+200=800"

if __name__ == '__main__':
    test_chunker()
    print("Chunker test passed!")
