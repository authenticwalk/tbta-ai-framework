#!/usr/bin/env python3
"""
Fine-tune OpenAI model on TBTA data.

Usage:
    python train_openai.py
    python train_openai.py --train data/openai/train.jsonl
    python train_openai.py --model gpt-4.1-mini-2025-04-14

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


def validate_jsonl(file_path: Path) -> tuple[bool, int, list[str]]:
    """Validate JSONL format."""
    errors = []
    count = 0
    
    with open(file_path, 'r') as f:
        for i, line in enumerate(f, 1):
            count += 1
            try:
                data = json.loads(line)
                if 'messages' not in data:
                    errors.append(f"Line {i}: Missing 'messages' key")
            except json.JSONDecodeError as e:
                errors.append(f"Line {i}: Invalid JSON: {e}")
    
    return len(errors) == 0, count, errors[:5]


def upload_and_train(client: OpenAI, train_path: Path, model: str, suffix: str):
    """Upload file and start fine-tuning job."""
    
    # Validate
    print(f"Validating {train_path}...")
    valid, count, errors = validate_jsonl(train_path)
    if not valid:
        print(f"Validation failed:")
        for e in errors:
            print(f"  {e}")
        sys.exit(1)
    print(f"  {count} examples validated")
    
    # Upload
    print(f"Uploading training file...")
    with open(train_path, 'rb') as f:
        file_response = client.files.create(file=f, purpose='fine-tune')
    print(f"  File ID: {file_response.id}")
    
    # Create job
    print(f"Creating fine-tuning job with {model}...")
    job = client.fine_tuning.jobs.create(
        training_file=file_response.id,
        model=model,
        suffix=suffix
    )
    print(f"  Job ID: {job.id}")
    
    # Monitor
    print(f"\nMonitoring job (Ctrl+C to stop, job continues in background)...\n")
    last_event = None
    
    try:
        while True:
            job = client.fine_tuning.jobs.retrieve(job.id)
            
            # Get new events
            events = client.fine_tuning.jobs.list_events(fine_tuning_job_id=job.id, limit=10)
            for event in reversed(events.data):
                if last_event is None or event.id > last_event:
                    print(f"  {event.message}")
                    last_event = event.id
            
            if job.status in ['succeeded', 'failed', 'cancelled']:
                break
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        print(f"\nStopped monitoring. Job {job.id} continues.")
        return job.id, None
    
    # Results
    print("\n" + "=" * 50)
    if job.status == 'succeeded':
        print(f"SUCCESS! Model: {job.fine_tuned_model}")
        
        # Save info
        info_path = train_path.parent / "job_info.json"
        with open(info_path, 'w') as f:
            json.dump({
                "job_id": job.id,
                "model": job.fine_tuned_model,
                "base_model": model,
                "completed_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }, f, indent=2)
        print(f"Saved to {info_path}")
        
        return job.id, job.fine_tuned_model
    else:
        print(f"FAILED: {job.status}")
        return job.id, None


def main():
    parser = argparse.ArgumentParser(description="Fine-tune OpenAI model")
    parser.add_argument("--train", "-t", type=Path, default=Path("data/openai/train.jsonl"))
    parser.add_argument("--model", "-m", default="gpt-4.1-mini-2025-04-14",
                        help="Base model (gpt-4.1-mini-2025-04-14, gpt-4.1-2025-04-14)")
    parser.add_argument("--suffix", "-s", default="tbta", help="Model suffix")
    args = parser.parse_args()
    
    if not os.environ.get('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not set")
        print("Run: export OPENAI_API_KEY='sk-...'")
        sys.exit(1)
    
    if not args.train.exists():
        print(f"Error: Training file not found: {args.train}")
        print("Run export_data.py first")
        sys.exit(1)
    
    client = OpenAI()
    upload_and_train(client, args.train, args.model, args.suffix)


if __name__ == "__main__":
    main()

