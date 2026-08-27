import argparse
import json
from pathlib import Path

from app.evaluation.metrics import (
    hit_rate_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Score RAG retrieval results from JSONL files.")
    parser.add_argument("score", nargs="?")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--k", type=int, default=5)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    dataset_lines = (line for line in args.dataset.read_text().splitlines() if line)
    dataset = {item["id"]: item for line in dataset_lines if (item := json.loads(line))}
    results = [json.loads(line) for line in args.results.read_text().splitlines() if line]
    scores = []
    for result in results:
        item = dataset[result["id"]]
        relevant = set(item["relevant_chunk_ids"])
        retrieved = result["retrieved_chunk_ids"]
        scores.append(
            {
                "recall_at_k": recall_at_k(retrieved, relevant, args.k),
                "precision_at_k": precision_at_k(retrieved, relevant, args.k),
                "hit_rate_at_k": hit_rate_at_k(retrieved, relevant, args.k),
                "mrr": reciprocal_rank(retrieved, relevant),
                "ndcg_at_k": ndcg_at_k(retrieved, relevant, args.k),
            }
        )
    report = (
        {key: sum(score[key] for score in scores) / len(scores) for key in scores[0]}
        if scores
        else {}
    )
    rendered = json.dumps(report, indent=2)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
