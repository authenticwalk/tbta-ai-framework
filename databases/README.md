# TBTA AI Framework

Modular SQLite databases for Bible translation AI, optimized for cross-database joins and semantic search.

## Overview

This project restructures TBTA (The Bible Translator's Assistant) data into normalized, joinable SQLite databases with vector embeddings for semantic search.

### Why This Structure?

| Benefit | Description |
|---------|-------------|
| **Modular** | Load only what you need (verses, concepts, NIV, etc.) |
| **Joinable** | SQLite `ATTACH` enables cross-database queries |
| **Searchable** | INT8 vector embeddings for semantic similarity |

## How to Rebuilt from older Format

```bash
# 1. Copy source databases to original/
cp /path/to/Bible.sqlite databases/original/
cp /path/to/Bible\ -\ NIV.sqlite databases/original/
cp /path/to/Ontology.sqlite databases/original/

# 2. Run conversion
python scripts/convert_db.py

# 3. Generate embeddings (requires sentence-transformers)
pip install sentence-transformers sqlite-vec apsw numpy pyyaml tqdm
python scripts/create_embeddings.py
```

## Directory Structure

```
tbta-ai-framework/
├── databases/
│   ├── original/           # Source databases (not in git)
│   │   ├── Bible.sqlite
│   │   ├── Bible - NIV.sqlite
│   │   └── Ontology.sqlite
│   ├── verses.sqlite       # Verses with node references
│   ├── nodes.sqlite        # Parsed word nodes
│   ├── niv.sqlite          # NIV translations
│   ├── concepts.sqlite     # Semantic concepts
│   └── strongs.sqlite      # Strong's lexicon
├── embeddings/
│   ├── verse_vectors.sqlite
│   ├── concept_vectors.sqlite
│   └── strongs_vectors.sqlite
└── scripts/
    ├── convert_db.py       # Database conversion
    ├── create_embeddings.py # Vector generation
    └── decode_analysis.py  # Parse AnalyzedVerse
```

## Database Schemas

### verses.sqlite

Verses with references to parsed nodes.

```sql
CREATE TABLE verses (
    reference TEXT PRIMARY KEY, -- GEN-001-001 format
    book CHAR(3) NOT NULL,      -- USFM3 code (GEN, MAT, etc.)
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    verse_text TEXT,            -- Paraphrased text
    node_ids JSON NOT NULL      -- Array of node IDs [1, 2, 3, ...]
);
CREATE INDEX idx_verses_book ON verses(book, chapter, verse);
```

### nodes.sqlite

Parsed word nodes from AnalyzedVerse with concept links.

```sql
CREATE TABLE nodes (
    node_id INTEGER PRIMARY KEY,
    category CHAR(1),           -- N=Noun, V=Verb, A=Adjective, etc.
    content TEXT,               -- Original word text
    stem TEXT,                  -- Normalized word form
    sense CHAR(1),              -- Lexical sense (A, B, C...)
    part_of_speech TEXT,        -- Noun, Verb, Adjective...
    feature_codes TEXT,         -- Full TBTA feature string
    concept_id INTEGER          -- FK to concepts.id
);
```

### niv.sqlite (or any version you want)

NIV Bible translations.

```sql
CREATE TABLE niv (
    reference TEXT PRIMARY KEY, -- GEN-001-001 format
    book CHAR(3) NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    text TEXT
);
CREATE INDEX idx_niv_book ON niv(book, chapter, verse);
```

### concepts.sqlite

Semantic concepts from the Ontology database with Strong's mappings.

```sql
CREATE TABLE concepts (
    id INTEGER,                 -- Concept ID (not unique - same stem has multiple senses)
    stem TEXT,                  -- Base word form
    sense TEXT,                 -- Sense identifier (A, B, C...)
    part_of_speech TEXT,        -- Noun, Verb, Adjective...
    gloss TEXT,                 -- Full definition
    brief_gloss TEXT,           -- Short definition
    occurrences INTEGER,        -- Frequency count
    categorization TEXT,        -- Category codes
    curated_examples TEXT,      -- Example usage
    level INTEGER,              -- Complexity level
    note TEXT,                  -- Additional notes
    strongs_mappings JSON       -- ["H1234", "G5678"] Strong's references
);
CREATE INDEX idx_concept_stem ON concepts(stem);
CREATE INDEX idx_concept_pos ON concepts(part_of_speech);
```

### strongs.sqlite

Strong's Hebrew/Greek lexicon.

```sql
CREATE TABLE strongs (
    strongs_number TEXT PRIMARY KEY,  -- H1234 or G5678
    language TEXT,                    -- Hebrew or Greek
    lemma TEXT,                       -- Original word
    definition TEXT,                  -- English definition
    derivation TEXT                   -- Etymology
);
```

### Embedding Databases

Vector embeddings using sqlite-vec with INT8 quantization (4x storage reduction).

```sql
-- verse_vectors.sqlite
CREATE VIRTUAL TABLE verse_vectors USING vec0(
    embedding int8[384],
    +book TEXT,
    +chapter INTEGER,
    +verse INTEGER
);

-- concept_vectors.sqlite
CREATE VIRTUAL TABLE concept_vectors USING vec0(
    embedding int8[384],
    +concept_id INTEGER,
    +stem TEXT
);

-- strongs_vectors.sqlite
CREATE VIRTUAL TABLE strongs_vectors USING vec0(
    embedding int8[384],
    +strongs_number TEXT
);
```

## Cross-Database Queries

SQLite's `ATTACH` enables powerful cross-database joins:

### Get verse with word meanings

```sql
ATTACH 'databases/nodes.sqlite' AS n;
ATTACH 'databases/concepts.sqlite' AS c;
ATTACH 'databases/niv.sqlite' AS niv;

SELECT 
    v.book, v.chapter, v.verse,
    niv.niv.text AS niv_text,
    n.nodes.content AS word,
    n.nodes.part_of_speech,
    c.concepts.gloss AS meaning
FROM verses v
JOIN json_each(v.node_ids) AS je
JOIN n.nodes ON n.nodes.node_id = je.value
LEFT JOIN c.concepts ON c.concepts.id = n.nodes.concept_id
LEFT JOIN niv.niv ON niv.niv.book = v.book 
    AND niv.niv.chapter = v.chapter 
    AND niv.niv.verse = v.verse
WHERE v.book = 'GEN' AND v.chapter = 1 AND v.verse = 1;
```

### Find verses containing a concept

```sql
ATTACH 'databases/nodes.sqlite' AS n;
ATTACH 'databases/concepts.sqlite' AS c;

SELECT DISTINCT v.book, v.chapter, v.verse, v.verse_text
FROM verses v
JOIN json_each(v.node_ids) AS je
JOIN n.nodes ON n.nodes.node_id = je.value
JOIN c.concepts ON c.concepts.id = n.nodes.concept_id
WHERE c.concepts.stem = 'love'
ORDER BY v.book, v.chapter, v.verse;
```

### Get all words with their concepts

```sql
ATTACH 'databases/concepts.sqlite' AS c;

SELECT 
    n.content AS word,
    n.part_of_speech,
    c.concepts.gloss AS definition,
    COUNT(*) as occurrences
FROM nodes n
LEFT JOIN c.concepts ON c.concepts.id = n.concept_id
WHERE n.content IS NOT NULL
GROUP BY n.content, n.part_of_speech, c.concepts.gloss
ORDER BY occurrences DESC
LIMIT 20;
```

## Semantic Search with Embeddings

### Setup

```python
import apsw
import sqlite_vec
import numpy as np
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Connect and load vec0 extension
db = apsw.Connection("embeddings/verse_vectors.sqlite")
db.enable_load_extension(True)
sqlite_vec.load(db)
```

### Find similar verses

```python
# Encode query
query = "God's love for humanity"
query_vec = model.encode(query, normalize_embeddings=True)
query_int8 = np.clip(query_vec * 127, -127, 127).astype(np.int8)

# Search
results = list(db.cursor().execute("""
    SELECT book, chapter, verse, distance
    FROM verse_vectors
    WHERE embedding MATCH vec_int8(?)
    ORDER BY distance
    LIMIT 10
""", [query_int8.tobytes()]))

for book, ch, vs, dist in results:
    print(f"{book} {ch}:{vs} (distance={dist:.3f})")
```

### Find similar concepts

```python
db = apsw.Connection("embeddings/concept_vectors.sqlite")
db.enable_load_extension(True)
sqlite_vec.load(db)

query = "salvation redemption forgiveness"
query_vec = model.encode(query, normalize_embeddings=True)
query_int8 = np.clip(query_vec * 127, -127, 127).astype(np.int8)

results = list(db.cursor().execute("""
    SELECT stem, concept_id, distance
    FROM concept_vectors
    WHERE embedding MATCH vec_int8(?)
    ORDER BY distance
    LIMIT 10
""", [query_int8.tobytes()]))
```

## Scripts

### convert_db.py

Converts source databases into normalized format.

```bash
python scripts/convert_db.py
```

### create_embeddings.py

Generates vector embeddings for semantic search.

```bash
# Full generation
python scripts/create_embeddings.py

# Skip Strong's if no YAML files
python scripts/create_embeddings.py --skip-strongs

# Use different model
python scripts/create_embeddings.py --model all-mpnet-base-v2
```

### decode_analysis.py

Parses AnalyzedVerse encoding into JSON structure.

```bash
# Parse verse to JSON
python scripts/decode_analysis.py "GEN 1:1" --pretty

# Save to file
python scripts/decode_analysis.py "JHN 3:16" --output john3-16.json

# Show raw encoding
python scripts/decode_analysis.py "MAT 5:3" --raw
```

## What are Embeddings?

Embeddings are numerical representations of text that capture semantic meaning. Similar texts have similar embeddings, enabling:

- **Semantic search**: Find verses about "love" even if they don't contain that word
- **Concept discovery**: Find related theological concepts
- **Cross-lingual**: Works across translations (English, Greek, Hebrew)

### Storage Efficiency

| Type | Size per vector | 35k vectors |
|------|-----------------|-------------|
| float32 | 1,536 bytes | 53 MB |
| **int8** | 384 bytes | **13 MB** |

We use INT8 quantization for 4x storage reduction with minimal accuracy loss.

## Size Estimates

| Database | Est. Size | Records |
|----------|-----------|---------|
| verses.sqlite | ~5 MB | 17.5k verses |
| nodes.sqlite | ~15 MB | ~500k nodes |
| niv.sqlite | ~3 MB | 30k verses |
| concepts.sqlite | ~1 MB | 5.7k concepts |
| strongs.sqlite | ~2 MB | 14k entries |
| verse_vectors.sqlite | ~7 MB | 17.5k embeddings |
| concept_vectors.sqlite | ~2 MB | 5.7k embeddings |
| strongs_vectors.sqlite | ~5 MB | 14k embeddings |
| **Total** | **~40 MB** | |

## Requirements

```bash
# Core (for convert_db.py)
pip install sqlite3  # Built into Python

# Embeddings (for create_embeddings.py)
pip install sentence-transformers sqlite-vec apsw numpy pyyaml tqdm torch
```

## License

MIT License - See LICENSE file.
