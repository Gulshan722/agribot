# eval/run_eval.py
"""
Run AgriBot evaluation against the golden dataset.
Exits with code 1 if any metric falls below threshold — used by CI.

Usage:
  python3 eval/run_eval.py              # run with default thresholds
  python3 eval/run_eval.py --threshold 0.75
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.retrieval.search import search
from src.generation.generator import generate_answer
from eval.metrics import compute_all_metrics
from src.utils.logger import get_logger

logger = get_logger(__name__)

THRESHOLDS = {
    "context_recall":    0.45,   # realistic for cross-vocab matching
    "answer_relevancy":  0.70,
    "mrr_at_5":          0.35,
}


def load_dataset(path: str = "data/eval/golden_dataset.json"):
    if not Path(path).exists():
        logger.error(f"Dataset not found at {path}")
        logger.error("Run: python3 eval/generate_eval_dataset.py")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def run_evaluation(threshold_override: float = None) -> dict:
    dataset = load_dataset()
    logger.info(f"Running eval on {len(dataset)} questions...")

    if threshold_override:
        for k in THRESHOLDS:
            THRESHOLDS[k] = threshold_override

    results = []
    all_scores = {k: [] for k in THRESHOLDS}

    for i, item in enumerate(dataset):
        question = item["question"]
        expected = item["expected_answer"]
        logger.info(f"[{i+1}/{len(dataset)}] {question}")

        try:
            # Retrieve
            chunks = search(question)

            # Generate
            gen_result = generate_answer(question, chunks)
            actual_answer = gen_result["answer"]

            # Score
            scores = compute_all_metrics(
                question, expected, actual_answer, chunks
            )

            for k, v in scores.items():
                all_scores[k].append(v)

            results.append({
                "id": item["id"],
                "question": question,
                "category": item.get("category", "general"),
                "scores": scores,
                "passed": all(
                    scores[k] >= THRESHOLDS[k] for k in THRESHOLDS
                )
            })

            status = "✅" if results[-1]["passed"] else "❌"
            logger.info(
                f"  {status} recall={scores['context_recall']:.2f} "
                f"relevancy={scores['answer_relevancy']:.2f} "
                f"mrr={scores['mrr_at_5']:.2f}"
            )

        except Exception as e:
            logger.error(f"  Failed: {e}")
            results.append({
                "id": item["id"],
                "question": question,
                "scores": {k: 0.0 for k in THRESHOLDS},
                "passed": False,
                "error": str(e)
            })

    # Compute averages
    averages = {
        k: round(sum(v) / len(v), 3) if v else 0.0
        for k, v in all_scores.items()
    }

    passed_count = sum(1 for r in results if r["passed"])
    total = len(results)
    overall_pass = all(averages[k] >= THRESHOLDS[k] for k in THRESHOLDS)

    report = {
        "timestamp": datetime.now().isoformat(),
        "total_questions": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "pass_rate": round(passed_count / total, 3),
        "averages": averages,
        "thresholds": THRESHOLDS,
        "overall_pass": overall_pass,
        "results": results
    }

    # Save report
    report_path = Path("data/eval/eval_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Print summary
    print("\n" + "="*55)
    print("AGRIBOT EVALUATION REPORT")
    print("="*55)
    print(f"Questions evaluated : {total}")
    print(f"Passed              : {passed_count}/{total} ({report['pass_rate']*100:.1f}%)")
    print()
    print("METRIC AVERAGES vs THRESHOLDS:")
    for metric, avg in averages.items():
        threshold = THRESHOLDS[metric]
        status = "✅ PASS" if avg >= threshold else "❌ FAIL"
        print(f"  {metric:<22} {avg:.3f}  (threshold: {threshold})  {status}")
    print()
    print(f"OVERALL: {'✅ PASSED' if overall_pass else '❌ FAILED'}")
    print("="*55)
    print(f"Full report saved to: {report_path}")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=float, default=None)
    args = parser.parse_args()

    report = run_evaluation(threshold_override=args.threshold)

    # Exit with error code if CI should fail
    if not report["overall_pass"]:
        logger.error("Evaluation FAILED — quality below threshold")
        sys.exit(1)
    else:
        logger.info("Evaluation PASSED")
        sys.exit(0)