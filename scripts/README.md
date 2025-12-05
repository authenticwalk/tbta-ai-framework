# TBTA AI Framework Scripts

Utility scripts for working with TBTA (Tabitha Bible Translation Assistant) data.

## Quick Start

The most useful scripts for common workflows:

| Script | Purpose | Example |
|--------|---------|---------|
| `lint_check.py` | **Convert linter errors to LLM-readable tips** | `python lint_check.py --serve` |
| `prepare_verse.py` | Prepare verse data for encoding | `python prepare_verse.py "John 3:16"` |
| `extraction/extract_feature.py` | Extract TBTA features from database | `python extraction/extract_feature.py --feature Aspect` |

## Key Script: lint_check.py

Converts the Tabitha checker API's JSON output into actionable, LLM-friendly reports.

```bash
# Run as local API server (recommended)
python lint_check.py --serve

# Check text directly
python lint_check.py --text "The man went home"

# Process existing file
python lint_check.py input/RUT-004-001.txt
```

**API Usage:**
```bash
# Check by verse reference
curl "http://localhost:5000/check?reference=1JN3-16"

# Check raw text
curl -X POST http://localhost:5000/check -d '{"text": "The man went home."}'
```

**Output transforms linter JSON into:**
- Errors grouped by word with fix suggestions
- Valid/invalid sense options for each word
- Specific hints (bracket quoted speech, add sense suffixes, etc.)

## Directory Structure

```
scripts/
├── README.md                    # This file
├── lint_check.py                # Linter → LLM tips converter
├── prepare_verse.py             # Verse data preparation
├── decode_analysis.py           # Parse TBTA AnalyzedVerse encoding
│
├── database/                    # Database utilities
│   └── convert_db.py            # Convert TBTA source databases
│
├── embeddings/                  # Vector embedding tools
│   ├── create_embeddings.py     # Generate sqlite-vec embeddings
│   ├── demo_embeddings.py       # Interactive embedding demos
│   └── compare_providers.py     # Compare local vs OpenAI models
│
├── extraction/                  # TBTA data extraction
│   ├── extract_feature.py       # Extract features (Aspect, Mood, etc.)
│   ├── extract_concepts.py      # Extract concepts for mapping
│   ├── tbta_processor.py        # Core TBTA processing logic
│   └── enrich_extract_with_verses.py
│
├── analysis/                    # Output analysis
│   ├── group_by_strongs.py      # Group results by Strong's number
│   └── group_by_reasons.py      # Group by linguistic reasons
│
├── strongs/                     # Strong's number utilities
│   └── extract_tbta_nodes.py    # Extract TBTA nodes for Strong's
│
├── validation/                  # Output validation
│   ├── validate_output.py       # Validate YAML output structure
│   └── score_baseline.py        # Score against baseline
│
└── add_strongs_to_concepts/     # Concept-Strong's mapping
    ├── README.md                # Process documentation
    ├── extract_concepts.py      # Export unmapped concepts
    └── apply_strongs.py         # Apply mappings to database
```

## Workflow Scripts

### 1. Preparing Verses for Encoding

```bash
# Single verse
python prepare_verse.py "Ruth 4:1"

# Verse range
python prepare_verse.py "Matthew 2:1-10"

# Entire chapter
python prepare_verse.py "John 3"
```

Creates two files in `input/`:
- `{REF}.txt` - NIV text + linter results for the LLM
- `{REF}.secret` - Reference solution (don't share with LLM)

### 2. Database Conversion

```bash
python database/convert_db.py --source-dir databases/original
```

Converts source TBTA databases into normalized SQLite files:
- `verses.sqlite` - Verses with node IDs
- `nodes.sqlite` - Normalized linguistic nodes
- `niv.sqlite` - NIV translations
- `concepts.sqlite` - Ontology concepts
- `strongs.sqlite` - Strong's lexicon

### 3. Embeddings

```bash
# Create local embeddings (no API key needed)
python embeddings/create_embeddings.py --provider local

# Create OpenAI embeddings (requires OPENAI_API_KEY)
python embeddings/create_embeddings.py --provider openai

# Interactive demo
python embeddings/demo_embeddings.py teach
python embeddings/demo_embeddings.py search "God's love"
```

### 4. Feature Extraction

```bash
# Extract all Aspect values
python extraction/extract_feature.py --feature Aspect

# Extract with sample verses
python extraction/extract_feature.py --feature Mood --samples 5
```

## Requirements

Core scripts require:
```
pyyaml
```

Embedding scripts additionally require:
```
sentence-transformers
sqlite-vec
apsw
numpy
tqdm
openai  # for OpenAI embeddings
```

## Tips

### Using lint_check.py with LLMs

The linter report format is designed for LLM consumption:

1. **Run as server**: `python lint_check.py --serve`
2. **Call from your code**: POST text to `http://localhost:5000/check`
3. **Feed the report to your LLM**: The report includes:
   - Specific errors with word context
   - Available sense options (e.g., `love_A`, `love_B`)
   - Actionable fix suggestions

Example report output:
```
# Linter Report: 1JN 3:16

**Status:** ERROR | 2 errors, 1 warning

## Errors to Fix

### `love`
**Errors:**
  - No valid case frame found
**Valid senses (can use):**
  - `love_A` (L0): to feel strong affection for
  - `love_B` (L1): to value highly
**Fix:** Append sense to word (e.g., `love_A`)
```

### Debugging AnalyzedVerse

```bash
python decode_analysis.py "GEN 1:1" --pretty
```

Decodes TBTA's character-based linguistic encoding into readable JSON.
