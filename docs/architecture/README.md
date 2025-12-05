# System Architecture

Developer guide to the TBTA AI Framework architecture.

## Overview

The framework consists of three main layers:

```
┌─────────────────────────────────────────────────────┐
│                    AI Layer                         │
│  prompts/predict-phase1/  →  Claude/OpenAI/local   │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                  Data Layer                         │
│  databases/*.sqlite  →  SQLite + sqlite-vec        │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│                 Script Layer                        │
│  scripts/*.py  →  Python tools                      │
└─────────────────────────────────────────────────────┘
```

## AI Layer

### Prompts

Located in `prompts/predict-phase1/`:

| File | Purpose |
|------|---------|
| CODEX-PROMPT.md | Main He1 encoder prompt |
| SKILL.md | Orchestration workflow |
| LEARN.md | Learning from mistakes |
| examples.md | Example encodings |

### Usage Pattern

```python
# 1. Load prompt
with open("prompts/predict-phase1/CODEX-PROMPT.md") as f:
    system_prompt = f.read()

# 2. Call AI with verse
response = ai.complete(
    system=system_prompt,
    user=f"Encode: {niv_verse}"
)

# 3. Validate output
errors = lint_check(response)
```

## Data Layer

### Database Schema

Six SQLite databases with normalized, joinable tables:

```
databases/
├── verses.sqlite       # Verses + node references
├── nodes.sqlite        # Parsed word nodes
├── concepts.sqlite     # Semantic concepts
├── strongs.sqlite      # Strong's lexicon
├── niv.sqlite          # NIV translations
└── embeddings/         # Vector databases
    ├── local/          # Local model embeddings
    └── openai/         # OpenAI embeddings
```

See [databases/README.md](../../databases/README.md) for full schema.

### Cross-Database Joins

SQLite `ATTACH` enables queries across databases:

```sql
ATTACH 'databases/nodes.sqlite' AS n;
ATTACH 'databases/concepts.sqlite' AS c;

SELECT v.reference, n.nodes.content, c.concepts.gloss
FROM verses v
JOIN json_each(v.node_ids) AS je
JOIN n.nodes ON n.nodes.node_id = je.value
LEFT JOIN c.concepts ON c.concepts.id = n.nodes.concept_id
WHERE v.book = 'JHN' AND v.chapter = 3 AND v.verse = 16;
```

### Vector Search

Using sqlite-vec with INT8 quantization:

```python
import apsw
import sqlite_vec
import numpy as np

# Connect
db = apsw.Connection("databases/embeddings/openai/concept_vectors.sqlite")
db.enable_load_extension(True)
sqlite_vec.load(db)

# Encode query
query_vec = encode("God's love")  # Your embedding function
query_int8 = np.clip(query_vec * 127, -127, 127).astype(np.int8)

# Search
results = db.cursor().execute("""
    SELECT stem, concept_id, distance
    FROM concept_vectors
    WHERE embedding MATCH vec_int8(?)
    ORDER BY distance
    LIMIT 10
""", [query_int8.tobytes()])
```

## Script Layer

### Core Scripts

| Script | Purpose |
|--------|---------|
| convert_db.py | Convert TBTA source databases |
| create_embeddings.py | Generate vector embeddings |
| demo_embeddings.py | Interactive embedding demo |
| lint_check.py | Validate He1 encoding |
| decode_analysis.py | Parse AnalyzedVerse |

### Embedding Pipeline

```bash
# 1. Convert source databases
python scripts/convert_db.py

# 2. Generate embeddings (choose provider)
python scripts/create_embeddings.py --provider local   # Free, local
python scripts/create_embeddings.py --provider openai  # Better quality

# 3. Test
python scripts/demo_embeddings.py search "salvation"
```

### Configuration

Scripts use project-relative paths:

```python
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_DIR = PROJECT_DIR / "databases"
EMB_DIR = DB_DIR / "embeddings"
```

## Extension Points

### Adding a New Embedding Provider

1. Add provider config in `create_embeddings.py`:
```python
PROVIDERS = {
    "local": {...},
    "openai": {...},
    "new_provider": {
        "default_model": "model-name",
        "default_dims": 512,
    }
}
```

2. Implement encode function
3. Create output directory: `databases/embeddings/new_provider/`

### Adding a New Database

1. Create table schema
2. Update `convert_db.py` extraction
3. Add embedding generation if needed
4. Document in `databases/README.md`

## Testing

```bash
# Run embedding demo
python scripts/demo_embeddings.py teach

# Compare providers
python scripts/compare_providers.py

# Validate encoding
python scripts/lint_check.py "test encoding"
```

## Dependencies

```bash
# Core
Python 3.10+
sqlite3 (built-in)

# Embeddings
pip install sentence-transformers  # Local models
pip install openai                 # OpenAI models
pip install sqlite-vec apsw        # Vector search
pip install numpy torch            # Computation

# Optional
pip install pyyaml tqdm            # Utilities
```

## Performance Notes

- INT8 embeddings: 4x storage reduction vs float32
- sqlite-vec: ~1ms search on 50k vectors
- Local models: ~10 vectors/second on CPU
- OpenAI: ~100 vectors/second (API limited)

## Related

- [databases/README.md](../../databases/README.md) - Database schema details
- [Phase 1 Encoding](../phase1-encoding/) - He1 encoding reference
- [Research](../../research/) - Feature documentation
