import sys
import os

# add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from query import search

def test_search():
    query = "What is Ayushman Bharat?"
    print(f"Testing search with query: {query}")
    result = search(query)
    print("\nResult:")
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_search()
