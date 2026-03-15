from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL

# load model once at startup so we dont reload on every call
print(f"Loading model: {EMBEDDING_MODEL}...")
model = SentenceTransformer(EMBEDDING_MODEL)
print(f"Model ready. Dimension: {model.get_sentence_embedding_dimension()}")


def generate_embedding(text):
    """converts text to a vector embedding"""
    if not text or not text.strip():
        raise ValueError("cant embed empty text")
    return model.encode(text).tolist()
