# tests/test_retrieval.py
from src.retrieval.search import search, format_results_for_display

TEST_QUERIES = [
    "how to manage drought stress in wheat crops",
    "what fertilizer should I use for rice paddy",
    "organic methods to control aphids on vegetables",
    "when to plant maize in rainy season",
    "how to improve soil health for farming",
]

def test_retrieval():
    for query in TEST_QUERIES:
        print(f"\n{'#'*60}")
        print(f"QUERY: {query}")
        print(f"{'#'*60}")

        results = search(query)
        print(format_results_for_display(results))
        print(f"\nTotal results returned: {len(results)}")

if __name__ == "__main__":
    test_retrieval()