# Embedding Scripts

Tools for semantic search using vector embeddings. Find verses, concepts, and Strong's entries by **meaning**, not just keywords.

## What Are Embeddings?

Embeddings convert text into numbers (vectors) that capture semantic meaning. Similar texts have similar vectors, enabling:

- **Semantic search**: Find verses about "love" even if they don't contain that word
- **Concept discovery**: Find related theological concepts
- **Cross-lingual**: Works across English, Greek, Hebrew

## Scripts

| Script | Purpose |
|--------|---------|
| `demo_embeddings.py` | Interactive learning and search tool |
| `create_embeddings.py` | Generate embedding databases |
| `compare_providers.py` | Benchmark local vs OpenAI embeddings |

## Quick Start

```bash
# Learn what embeddings are (interactive)
python scripts/embeddings/demo_embeddings.py teach

# Search for concepts by meaning
python scripts/embeddings/demo_embeddings.py search "God's mercy"

# Analyze a verse word-by-word
python scripts/embeddings/demo_embeddings.py analyze "The Lord is my shepherd"
```

## demo_embeddings.py

Interactive CLI for learning and using embeddings.

### Modes

| Mode | Description |
|------|-------------|
| `teach` | Interactive tutorial explaining embeddings with examples |
| `search "text"` | Find concepts matching your search phrase |
| `analyze "verse"` | Word-by-word concept matching for a verse |
| `match` | Suggest Strong's numbers for unmapped concepts |
| `experiment` | Compare embedding strategies (word vs word+definition) |
| `compare` | Compare different embedding models |

### Examples

```bash
# Interactive embeddings tutorial
python scripts/embeddings/demo_embeddings.py teach

# Find concepts related to salvation
python scripts/embeddings/demo_embeddings.py search "salvation redemption"

# See what concepts match each word
python scripts/embeddings/demo_embeddings.py analyze "For God so loved the world"

# Use OpenAI embeddings instead of local
python scripts/embeddings/demo_embeddings.py --provider openai search "grace"
```

## create_embeddings.py

Generates vector embeddings for verses, concepts, and Strong's entries.

```bash
# Generate all embeddings (local model)
python scripts/embeddings/create_embeddings.py

# Use OpenAI embeddings
export OPENAI_API_KEY="sk-..."
python scripts/embeddings/create_embeddings.py --provider openai

# Skip Strong's if you don't have YAML files
python scripts/embeddings/create_embeddings.py --skip-strongs
```

Output goes to `databases/embeddings/{provider}/`:
- `verse_vectors.sqlite`
- `concept_vectors.sqlite`
- `strongs_vectors.sqlite`

## compare_providers.py

Benchmarks embedding providers on biblical term clustering.

```bash
# Compare local vs OpenAI on biblical vocabulary
python scripts/embeddings/compare_providers.py

# Test with realistic overlapping definitions
python scripts/embeddings/compare_providers.py --overlap
```

Tests 20+ semantic groups (Love, Faith, Sin, Salvation, etc.) across:
- English, Greek, Hebrew, Swahili, Indonesian
- Word-only vs word+definition strategies

## Requirements

```bash
pip install sentence-transformers sqlite-vec apsw numpy tqdm

# For OpenAI embeddings
pip install openai
export OPENAI_API_KEY="sk-..."
```

## Storage Efficiency

We use INT8 quantization for 4x storage reduction:

| Type | Size per vector | 35k vectors |
|------|-----------------|-------------|
| float32 | 1,536 bytes | 53 MB |
| **int8** | 384 bytes | **13 MB** |

## Embedding Providers

| Provider | Model | Dims | Notes |
|----------|-------|------|-------|
| `local` | paraphrase-multilingual-MiniLM-L12-v2 | 384 | Free, works offline, good multilingual |
| `openai` | text-embedding-3-small | 512 | Higher quality, requires API key |

The multilingual local model performs well on biblical terms (90% accuracy on our test set) and handles Greek/Hebrew text.
