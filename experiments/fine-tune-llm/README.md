# TBTA Fine-tuning

Fine-tune LLMs to predict TBTA semantic encodings from Bible verse references.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Export training data (requires Bible_unified.sqlite)
python export_data.py /path/to/Bible_unified.sqlite

# Train with OpenAI
export OPENAI_API_KEY='sk-...'
python train_openai.py

# Or train with Google Vertex AI
python train_google.py --project YOUR_PROJECT --bucket YOUR_BUCKET
```

## Files

| File | Purpose |
|------|---------|
| `export_data.py` | Extract training data from database |
| `train_openai.py` | Fine-tune with OpenAI API |
| `train_google.py` | Fine-tune with Google Vertex AI |
| `evaluate.py` | Evaluate model on holdout set |

## Data Format

Training data is exported in two formats:
- `data/openai/` - OpenAI chat format (`messages` array)
- `data/google/` - Google Vertex AI format (`contents` array)

---

## OpenAI Setup

1. Get API key from https://platform.openai.com/api-keys
2. Set environment variable:
   ```bash
   export OPENAI_API_KEY='sk-...'
   ```
3. Run training:
   ```bash
   python train_openai.py
   ```

---

## Google Vertex AI Setup

### Prerequisites

1. **Install Google Cloud SDK**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk
   ```

2. **Create GCP project** at https://console.cloud.google.com
   - Enable billing
   - Enable Vertex AI API:
     ```bash
     gcloud services enable aiplatform.googleapis.com
     ```

3. **Authenticate**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

4. **Create Cloud Storage bucket**
   ```bash
   gsutil mb -l us-central1 gs://your-bucket-name
   ```

### Run Training

```bash
python train_google.py --project YOUR_PROJECT --bucket YOUR_BUCKET

# Or with environment variables
export GOOGLE_CLOUD_PROJECT='your-project'
export GCS_BUCKET='your-bucket'
python train_google.py
```

### Supported Models

| Model | Notes |
|-------|-------|
| `gemini-2.0-flash-001` | Default, proven |
| `gemini-2.5-flash` | Newer, fast |
| `gemini-2.5-pro` | Most capable |

---

## Cost Estimate

| Platform | Model | ~Cost |
|----------|-------|-------|
| OpenAI | gpt-4.1-mini | $8-15 |
| Google | gemini-2.0-flash | $5-10 |

