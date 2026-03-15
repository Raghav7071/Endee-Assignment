"""
chunker.py — Simple text chunking utility for generating embeddings.
"""

def chunk_text(text, chunk_size=800, overlap=100):
    """
    Splits text into smaller chunks of given max length, with overlap.
    """
    if not text:
        return []
    
    words = text.split()
    chunks = []
    
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            
            # Keep the overlap amount of words from the end
            overlap_words = []
            overlap_len = 0
            for w in reversed(current_chunk):
                if overlap_len + len(w) + 1 <= overlap:
                    overlap_words.insert(0, w)
                    overlap_len += len(w) + 1
                else:
                    break
            
            current_chunk = overlap_words
            current_length = overlap_len
        
        current_chunk.append(word)
        current_length += len(word) + 1  # +1 for space
        
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks
