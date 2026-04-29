"""
ShopMind RAG Evaluation
Uses RAGAS to score retrieval faithfulness and answer relevancy.
Run: python scripts/eval.py

Demonstrates production-quality RAG evaluation — a key differentiator
for this NVIDIA DevRel role.
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))

# Test queries with ground truth for evaluation
EVAL_DATASET = [
    {
        "question": "Best noise-canceling headphones under $300",
        "ground_truth": "The Sony WH-1000XM5 at $279.99 and Sennheiser Momentum 4 at $279.95 are the top noise-canceling headphones under $300, both with industry-leading ANC.",
    },
    {
        "question": "Smartwatch for marathon runners",
        "ground_truth": "The Garmin Fenix 7X Solar is the best smartwatch for marathon runners with 28-day battery, GPS, and advanced training metrics at $749.99.",
    },
    {
        "question": "Budget wireless earbuds under $100 with ANC",
        "ground_truth": "The Jabra Elite 4 Active at $79.99 offers ANC, IP57 protection, and 28-hour total battery life making it the best ANC earbuds under $100.",
    },
    {
        "question": "Professional laptop for machine learning under $2000",
        "ground_truth": "The MacBook Pro 14 M3 Pro at $1999 or Dell XPS 15 with RTX 4060 at $1799.99 are top choices for ML engineers needing GPU acceleration.",
    },
    {
        "question": "Lightweight business laptop for travel",
        "ground_truth": "The Lenovo ThinkPad X1 Carbon at $1499 weighs only 2.48 lbs with MIL-SPEC durability and 15-hour battery, making it the best travel business laptop.",
    },
]


async def run_evaluation():
    """Run RAG pipeline evaluation using RAGAS metrics."""
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, answer_relevancy, context_recall
        from datasets import Dataset
    except ImportError:
        print("Install ragas and datasets: pip install ragas datasets")
        return

    from agent import ShopMindAgent

    print("Initializing ShopMind agent...")
    agent = ShopMindAgent()
    await agent.initialize()

    results = []
    print(f"\nRunning {len(EVAL_DATASET)} eval queries...\n")

    for i, item in enumerate(EVAL_DATASET):
        print(f"[{i+1}/{len(EVAL_DATASET)}] {item['question'][:60]}...")
        try:
            result = await agent.run(item["question"])
            results.append({
                "question": item["question"],
                "answer": result["answer"],
                "contexts": [s.get("name", "") for s in result["sources"]],
                "ground_truth": item["ground_truth"],
            })
        except Exception as e:
            print(f"  Error: {e}")
            results.append({
                "question": item["question"],
                "answer": "Error",
                "contexts": [],
                "ground_truth": item["ground_truth"],
            })

    dataset = Dataset.from_list(results)

    print("\nComputing RAGAS metrics...")
    scores = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_recall],
    )

    print("\n" + "="*50)
    print("SHOPMIND RAG EVALUATION RESULTS")
    print("="*50)
    print(f"Faithfulness:      {scores['faithfulness']:.3f}  (grounded in retrieved docs)")
    print(f"Answer Relevancy:  {scores['answer_relevancy']:.3f}  (answers the question)")
    print(f"Context Recall:    {scores['context_recall']:.3f}  (retrieves relevant context)")
    print("="*50)
    print(f"\nOverall RAG Score: {(scores['faithfulness'] + scores['answer_relevancy'] + scores['context_recall']) / 3:.3f}")
    print("\nNote: Scores above 0.80 indicate production-ready RAG quality.")

    return scores


if __name__ == "__main__":
    asyncio.run(run_evaluation())
