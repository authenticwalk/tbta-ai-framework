#!/usr/bin/env python3
"""
Evaluate fine-tuned model on holdout set.

Usage:
    python evaluate.py MODEL_NAME
    python evaluate.py ft:gpt-4.1-mini:tbta:xxx --holdout data/openai/holdout.jsonl
    python evaluate.py MODEL_NAME --sample 50

Requires: OPENAI_API_KEY environment variable
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai not installed. Run: pip install openai")
    sys.exit(1)


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate edit distance."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    prev = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (c1 != c2)))
        prev = curr
    return prev[-1]


def word_overlap(s1: str, s2: str) -> float:
    """Calculate word Jaccard similarity."""
    w1, w2 = set(s1.lower().split()), set(s2.lower().split())
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)


def load_holdout(path: Path) -> list[dict]:
    """Load holdout examples."""
    examples = []
    with open(path, 'r') as f:
        for line in f:
            data = json.loads(line)
            msgs = data['messages']
            examples.append({
                'system': msgs[0]['content'],
                'reference': msgs[1]['content'],
                'expected': msgs[2]['content'],
            })
    return examples


def evaluate(model: str, holdout_path: Path, sample_size: int = None, output_dir: Path = None):
    """Run evaluation."""
    client = OpenAI()
    examples = load_holdout(holdout_path)
    
    if sample_size and sample_size < len(examples):
        import random
        random.seed(42)
        examples = random.sample(examples, sample_size)
    
    print(f"Evaluating {len(examples)} examples with {model}...")
    
    results = []
    for i, ex in enumerate(examples):
        if i % 10 == 0:
            print(f"  {i}/{len(examples)}")
        
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": ex['system']},
                    {"role": "user", "content": ex['reference']},
                ],
                max_tokens=1000,
                temperature=0,
            )
            predicted = resp.choices[0].message.content
            expected = ex['expected']
            
            results.append({
                'reference': ex['reference'],
                'expected': expected,
                'predicted': predicted,
                'exact_match': predicted.strip() == expected.strip(),
                'word_overlap': word_overlap(predicted, expected),
                'edit_distance': levenshtein_distance(predicted, expected) / max(len(predicted), len(expected), 1),
            })
        except Exception as e:
            results.append({'reference': ex['reference'], 'error': str(e)})
        
        time.sleep(0.1)
    
    # Calculate metrics
    successful = [r for r in results if 'error' not in r]
    metrics = {
        'model': model,
        'total': len(examples),
        'successful': len(successful),
        'exact_matches': sum(1 for r in successful if r['exact_match']),
        'avg_word_overlap': sum(r['word_overlap'] for r in successful) / len(successful) if successful else 0,
        'avg_edit_distance': sum(r['edit_distance'] for r in successful) / len(successful) if successful else 0,
    }
    metrics['exact_match_rate'] = metrics['exact_matches'] / len(successful) if successful else 0
    
    # Print results
    print("\n" + "=" * 50)
    print(f"Model: {model}")
    print(f"Examples: {metrics['successful']}/{metrics['total']}")
    print(f"\nExact Match Rate: {metrics['exact_match_rate']:.1%}")
    print(f"Avg Word Overlap: {metrics['avg_word_overlap']:.1%}")
    print(f"Avg Edit Distance: {metrics['avg_edit_distance']:.3f}")
    
    # Show samples
    print("\n" + "-" * 50)
    print("SAMPLES:")
    for i, r in enumerate(successful[:3]):
        print(f"\n[{i+1}] {r['reference']}")
        print(f"  Expected: {r['expected'][:100]}...")
        print(f"  Predicted: {r['predicted'][:100]}...")
        print(f"  Overlap: {r['word_overlap']:.1%}")
    
    # Save results
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "metrics.json", 'w') as f:
            json.dump(metrics, f, indent=2)
        with open(output_dir / "results.jsonl", 'w') as f:
            for r in results:
                f.write(json.dumps(r) + '\n')
        print(f"\nSaved to {output_dir}")
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate fine-tuned model")
    parser.add_argument("model", help="Model name (e.g., ft:gpt-4.1-mini:tbta:xxx)")
    parser.add_argument("--holdout", type=Path, default=Path("data/openai/holdout.jsonl"))
    parser.add_argument("--sample", type=int, help="Sample size (for quick test)")
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    
    if not os.environ.get('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not set")
        sys.exit(1)
    
    if not args.holdout.exists():
        print(f"Error: Holdout file not found: {args.holdout}")
        sys.exit(1)
    
    evaluate(args.model, args.holdout, args.sample, args.output)


if __name__ == "__main__":
    main()

