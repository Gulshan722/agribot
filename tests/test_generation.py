# tests/test_generation.py
from src.agribot import ask

def test_agribot():
    queries = [
        "how to manage drought stress in wheat crops",
        "what fertilizer should I use for rice paddy",
        "how to improve soil health for farming",
    ]

    for query in queries:
        print(f"\n{'='*65}")
        print(f"FARMER ASKS: {query}")
        print(f"{'='*65}")

        result = ask(query, run_faithfulness_check=True)

        print(f"\nANSWER:\n{result['answer']}")

        print(f"\nCITATIONS ({result['num_sources'] if 'num_sources' in result else len(result['citations'])}):")
        for c in result["citations"]:
            print(f"  [{c['number']}] {c['source']} — page {c['page']}")

        if result["faithfulness"]:
            f = result["faithfulness"]
            status = "PASSED" if not result["flagged"] else "FLAGGED"
            print(f"\nFAITHFULNESS CHECK: {status}")
            print(f"  Score : {f['score']}")
            print(f"  Issues: {f['issues']}")

if __name__ == "__main__":
    test_agribot()