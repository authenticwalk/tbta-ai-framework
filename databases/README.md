# TBTA Databases

Modular SQLite databases optimized for AI-powered Bible translation tools.

## Why We Restructured the Databases

The original TBTA databases (Bible.sqlite, Ontology.sqlite) are monolithic and deeply nested. This made it hard to:

- **Query across data types** — Finding all verses with a concept required complex joins within a single database
- **Add AI features** — Embedding vectors need their own optimized storage
- **Share selectively** — You had to download everything, even if you only needed concepts

### What's Different Now

| Before (Monolithic) | After (Modular) |
|---------------------|-----------------|
| Everything in 2-3 large databases | Purpose-built databases you can mix-and-match |
| Complex nested queries | Simple `ATTACH` and join |
| No semantic search | INT8 embeddings for fast similarity search |
| All or nothing | Load only what you need |

### Practical Benefits

1. **"Find verses about X"** — Semantic search finds related verses even without exact keyword matches
2. **"What Strong's numbers relate to this concept?"** — Direct queries, no manual lookup
3. **"Show me word meanings for Genesis 1:1"** — One query joins verses → nodes → concepts
4. **Mix your own translations** — Add `kjv.sqlite`, `nlt.sqlite` alongside NIV

## Directory Structure

```
databases/
├── verses.sqlite         # Verse references + word nodes
├── nodes.sqlite          # Parsed words with part-of-speech, concepts
├── concepts.sqlite       # Semantic concepts with definitions
├── strongs.sqlite        # Strong's Hebrew/Greek lexicon
├── embeddings/           # Vector embeddings for semantic search
│   ├── local/            # Open-source model (works offline)
│   │   ├── verse_vectors.sqlite
│   │   ├── concept_vectors.sqlite
│   │   └── strongs_vectors.sqlite
│   └── openai/           # OpenAI embeddings (higher quality)
│       └── ...
└── original/             # Source databases (not in git)
```

## Quick Start: Useful Queries

### What words are in John 3:16?

```sql
ATTACH 'nodes.sqlite' AS n;
ATTACH 'concepts.sqlite' AS c;

SELECT 
    n.nodes.content AS word,
    n.nodes.part_of_speech,
    c.concepts.gloss AS meaning
FROM verses v
JOIN json_each(v.node_ids) AS j
JOIN n.nodes ON n.nodes.node_id = j.value
LEFT JOIN c.concepts ON c.concepts.id = n.nodes.concept_id
WHERE v.reference = 'JHN-003-016';
```

### Find all verses containing a concept

```sql
ATTACH 'nodes.sqlite' AS n;
ATTACH 'concepts.sqlite' AS c;

SELECT DISTINCT v.reference, v.verse_text
FROM verses v
JOIN json_each(v.node_ids) AS j
JOIN n.nodes ON n.nodes.node_id = j.value
JOIN c.concepts ON c.concepts.id = n.nodes.concept_id
WHERE c.concepts.stem = 'love'
ORDER BY v.reference;
```

### Get Strong's numbers for a concept

```sql
SELECT stem, sense, gloss, strongs_mappings
FROM concepts
WHERE stem = 'love' AND strongs_mappings IS NOT NULL;
```

### What concepts link to a Strong's number?

```sql
SELECT stem, sense, brief_gloss
FROM concepts
WHERE strongs_mappings LIKE '%H157%';  -- Hebrew "ahab" (love)
```

## Semantic Search with Embeddings

Embeddings let you search by **meaning**, not just keywords.

**New to embeddings?** Run the interactive tutorial:

```bash
python scripts/demo_embeddings.py teach
```

This walks you through what embeddings are and lets you experiment with word similarity.

### Find verses semantically similar to a phrase

```python
import apsw
import sqlite_vec
import numpy as np
from sentence_transformers import SentenceTransformer

# Load model and connect
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
db = apsw.Connection("databases/embeddings/local/verse_vectors.sqlite")
db.enable_load_extension(True)
sqlite_vec.load(db)

# Search for verses about "God's love for humanity"
query = "God's love for humanity"
query_vec = model.encode(query, normalize_embeddings=True)
query_int8 = np.clip(query_vec * 127, -127, 127).astype(np.int8)

results = db.cursor().execute("""
    SELECT book, chapter, verse, distance
    FROM verse_vectors
    WHERE embedding MATCH vec_int8(?)
    ORDER BY distance
    LIMIT 10
""", [query_int8.tobytes()])

for book, ch, vs, dist in results:
    print(f"{book} {ch}:{vs} (similarity: {1-dist/255:.2f})")
```

### Find concepts similar to a search phrase

```bash
# CLI search
python scripts/demo_embeddings.py search "salvation and redemption"

# Word-by-word verse analysis
python scripts/demo_embeddings.py analyze "For God so loved the world"
```

### Other demo modes

```bash
# Compare how different embedding strategies perform
python scripts/demo_embeddings.py experiment

# Match unmapped concepts to Strong's numbers
python scripts/demo_embeddings.py match

# Compare local vs OpenAI embeddings
python scripts/compare_providers.py
```

## Database Schemas

### verses.sqlite

```sql
CREATE TABLE verses (
    reference TEXT PRIMARY KEY,  -- JHN-003-016 format
    book CHAR(3) NOT NULL,       -- USFM3 code
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    verse_text TEXT,             -- Paraphrased text
    node_ids JSON NOT NULL       -- [1, 2, 3, ...] links to nodes
);
```

### nodes.sqlite

```sql
CREATE TABLE nodes (
    node_id INTEGER PRIMARY KEY,
    category CHAR(1),            -- N=Noun, V=Verb, etc.
    content TEXT,                -- Original word
    stem TEXT,                   -- Normalized form
    sense CHAR(1),               -- Lexical sense (A, B, C...)
    part_of_speech TEXT,
    feature_codes TEXT,          -- Full TBTA feature string
    concept_id INTEGER           -- FK to concepts.id
);
```

### concepts.sqlite

```sql
CREATE TABLE concepts (
    id INTEGER,
    stem TEXT,
    sense TEXT,
    part_of_speech TEXT,
    gloss TEXT,                  -- Full definition
    brief_gloss TEXT,            -- Short definition
    occurrences INTEGER,
    strongs_mappings JSON        -- ["H1234", "G5678"]
);
```

### strongs.sqlite

```sql
CREATE TABLE strongs (
    strongs_number TEXT PRIMARY KEY,  -- H1234 or G5678
    language TEXT,                    -- hebrew or greek
    lemma TEXT,                       -- Original word
    definition TEXT,
    derivation TEXT
);
```

### Embedding tables (sqlite-vec)

```sql
-- verse_vectors.sqlite
CREATE VIRTUAL TABLE verse_vectors USING vec0(
    embedding int8[384],  -- or int8[512] for OpenAI
    +book TEXT,
    +chapter INTEGER,
    +verse INTEGER
);
```

## Rebuilding from Original Databases

If you have the original TBTA databases:

```bash
# 1. Copy source databases
cp /path/to/Bible.sqlite databases/original/
cp /path/to/Ontology.sqlite databases/original/

# 2. Convert to modular format
python scripts/convert_db.py

# 3. Generate embeddings
pip install sentence-transformers sqlite-vec apsw numpy tqdm
python scripts/create_embeddings.py
```

## Size Comparison

| Database | Size | Records |
|----------|------|---------|
| verses.sqlite | ~5 MB | 17.5k verses |
| nodes.sqlite | ~15 MB | ~500k nodes |
| concepts.sqlite | ~1 MB | 5.7k concepts |
| strongs.sqlite | ~2 MB | 14k entries |
| embeddings (local) | ~14 MB | all vectors |
| **Total** | **~40 MB** | |

INT8 quantization gives 4x storage reduction with minimal accuracy loss.

## Requirements

```bash
# Core queries (Python 3.8+)
# sqlite3 is built into Python

# Semantic search
pip install sentence-transformers sqlite-vec apsw numpy tqdm
```

## Learn More

- **Embeddings tutorial**: `python scripts/demo_embeddings.py teach`
- **Compare providers**: `python scripts/compare_providers.py`
- **Conversion script**: `python scripts/convert_db.py --help`
