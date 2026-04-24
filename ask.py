# ask.py — interactive AgriBot terminal
import sys
sys.path.insert(0, '.')
from src.agribot import ask

print("=" * 55)
print("  AgriBot — Agricultural Knowledge Assistant")
print("  Type your farming question. 'quit' to exit.")
print("=" * 55)

while True:
    print()
    query = input("🌾 Your question: ").strip()

    if query.lower() in ["quit", "exit", "q"]:
        print("Goodbye! Happy farming! 🌱")
        break

    if not query:
        continue

    print("\n⏳ Searching knowledge base...\n")
    result = ask(query, run_faithfulness_check=False)

    print("─" * 55)
    print("ANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    for c in result["citations"]:
        print(f"  [{c['number']}] {c['source']} — page {c['page']}")

    print("─" * 55)