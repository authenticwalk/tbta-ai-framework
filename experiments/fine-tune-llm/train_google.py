#!/usr/bin/env python3
"""
Fine-tune Gemini on Google Vertex AI.

Usage:
    python train_google.py --project YOUR_PROJECT --bucket YOUR_BUCKET
    python train_google.py --project YOUR_PROJECT --bucket YOUR_BUCKET --model gemini-2.5-flash

Environment variables (alternative to CLI):
    GOOGLE_CLOUD_PROJECT - GCP project ID
    GCS_BUCKET - Cloud Storage bucket name
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

try:
    from google import genai
    from google.genai.types import CreateTuningJobConfig, HttpOptions, TuningDataset
except ImportError:
    print("Error: google-genai not installed. Run: pip install google-genai")
    sys.exit(1)

try:
    from google.cloud import storage
except ImportError:
    print("Error: google-cloud-storage not installed. Run: pip install google-cloud-storage")
    sys.exit(1)


def check_auth() -> bool:
    """Check if gcloud is authenticated."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def upload_to_gcs(local_path: Path, bucket_name: str, blob_name: str) -> str:
    """Upload file to Cloud Storage."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    print(f"Uploading {local_path.name} to gs://{bucket_name}/{blob_name}...")
    blob.upload_from_filename(str(local_path))
    
    return f"gs://{bucket_name}/{blob_name}"


def run_finetune(
    project_id: str,
    bucket_name: str,
    train_file: Path,
    validation_file: Path = None,
    model_name: str = "gemini-2.0-flash-001",
    display_name: str = "TBTA-Predictor",
    region: str = "us-central1",
):
    """Run fine-tuning job."""
    
    # Upload to GCS
    timestamp = int(time.time())
    train_uri = upload_to_gcs(train_file, bucket_name, f"finetune/{timestamp}/train.jsonl")
    
    val_uri = None
    if validation_file and validation_file.exists():
        val_uri = upload_to_gcs(validation_file, bucket_name, f"finetune/{timestamp}/validation.jsonl")
    
    # Initialize client
    print(f"\nConnecting to Vertex AI ({project_id}, {region})...")
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=region,
        http_options=HttpOptions(api_version="v1beta1")
    )
    
    # Create job
    config = {"tuned_model_display_name": display_name}
    if val_uri:
        config["validation_dataset"] = TuningDataset(gcs_uri=val_uri)
    
    print(f"Starting fine-tuning with {model_name}...")
    job = client.tunings.tune(
        base_model=model_name,
        training_dataset=TuningDataset(gcs_uri=train_uri),
        config=CreateTuningJobConfig(**config),
    )
    
    print(f"  Job: {job.name}")
    print(f"  State: {job.state}")
    
    # Poll for completion
    print("\nWaiting for completion (polling every 60s)...")
    running = {"JOB_STATE_PENDING", "JOB_STATE_RUNNING"}
    
    while job.state in running:
        time.sleep(60)
        job = client.tunings.get(name=job.name)
        print(f"  {job.state}")
    
    # Results
    print("\n" + "=" * 50)
    if job.state == "JOB_STATE_SUCCEEDED":
        print(f"SUCCESS!")
        print(f"  Model: {job.tuned_model.model}")
        print(f"  Endpoint: {job.tuned_model.endpoint}")
        
        # Save info
        info = {
            "model": job.tuned_model.model,
            "endpoint": job.tuned_model.endpoint,
            "base_model": model_name,
            "training_data": train_uri,
        }
        info_path = train_file.parent / "google_job_info.json"
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        print(f"  Saved to {info_path}")
        
        return job.tuned_model.endpoint
    else:
        print(f"FAILED: {job.state}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Fine-tune Gemini on Vertex AI")
    parser.add_argument("--project", "-p", default=os.environ.get("GOOGLE_CLOUD_PROJECT"),
                        help="GCP project ID")
    parser.add_argument("--bucket", "-b", default=os.environ.get("GCS_BUCKET"),
                        help="GCS bucket name")
    parser.add_argument("--train", "-t", type=Path, default=Path("data/google/train.jsonl"))
    parser.add_argument("--validation", "-v", type=Path, default=None)
    parser.add_argument("--model", "-m", default="gemini-2.0-flash-001",
                        choices=["gemini-2.0-flash-001", "gemini-2.0-flash", "gemini-2.5-flash",
                                 "gemini-2.5-pro", "gemini-2.5-flash-lite"])
    parser.add_argument("--name", "-n", default="TBTA-Predictor")
    parser.add_argument("--region", "-r", default="us-central1")
    args = parser.parse_args()
    
    if not args.project:
        print("Error: --project required (or set GOOGLE_CLOUD_PROJECT)")
        sys.exit(1)
    if not args.bucket:
        print("Error: --bucket required (or set GCS_BUCKET)")
        sys.exit(1)
    
    if not check_auth():
        print("Error: Not authenticated. Run:")
        print("  gcloud auth application-default login")
        sys.exit(1)
    
    if not args.train.exists():
        print(f"Error: Training file not found: {args.train}")
        print("Run export_data.py first")
        sys.exit(1)
    
    # Default validation to holdout in same directory
    if args.validation is None:
        args.validation = args.train.parent / "holdout.jsonl"
    
    run_finetune(
        project_id=args.project,
        bucket_name=args.bucket,
        train_file=args.train,
        validation_file=args.validation if args.validation.exists() else None,
        model_name=args.model,
        display_name=args.name,
        region=args.region,
    )


if __name__ == "__main__":
    main()

