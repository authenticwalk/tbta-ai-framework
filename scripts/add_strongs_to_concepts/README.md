# Concept-to-Strong's Mapping

Maps TBTA semantic concepts to Strong's lexical numbers.

## Overview

TBTA concepts are semantic units (like "abandon", "love", "king") that need to be linked to Strong's concordance numbers for cross-referencing with Biblical source languages.

## Current Status

| Metric | Count |
|--------|-------|
| Total concepts | 3,578 |
| With strongs | 2,233 (62%) |
| Without strongs | 1,345 |

## Process

### Step 1: Extract Concepts

```bash
python3 scripts/extract_concepts.py -o concepts_to_map.tsv
```

Outputs TSV with columns: `id, stem, gloss, part_of_speech, current_strongs, skip_reason`

Concepts are auto-skipped if they are:
- Numbers (`1`, `100`, `10th`)
- Dates (`100AD`, `167BC`)
- Grammar markers (stem starts with `-`)
- DELETE markers
- Conjunctions (`and`, `or`, `but`)
- Transliterations

### Step 2: Add Strongs Mappings

Use AI or manual review to add strongs mappings. See `ADD-STRONGS.md` for the complete AI prompt.

The mapping approach:
1. Search strongs definitions for the concept stem
2. Prioritize "to {stem}" for verbs, "a/an {stem}" for nouns
3. Filter out proper names and places
4. Limit to 5 best matches per concept

### Step 3: Apply Mappings

```bash
python3 scripts/apply_strongs.py concepts_with_strongs.tsv --clear-first
```

Input TSV must have columns: `id, stem, gloss, strongs_list`
- `strongs_list` is comma-separated (e.g., `G0025,H0157`)

## Known Weaknesses

### 1. Definition-Based Matching Limitations
- Only matches when concept stem appears in Strong's definition text
- Misses synonyms (e.g., "big" won't match "great" or "large")
- Misses related concepts without shared vocabulary

### 2. Compound Word Priority Issues
- "water" may match "water-jar" (H5035) before "water" (H4325)
- Definitions like "a water-ox" match before simple "water"

### 3. Missing Mappings (38%)
- Many concepts have no matching strongs definitions
- Abstract concepts, complex phrases, and idioms often unmatched
- Proper nouns intentionally excluded but some may be wanted

### 4. No Semantic Verification
- Mapping is purely text-based, no semantic similarity check
- "fire" concept may match "fire-pot" which is semantically different

### 5. Hebrew/Greek Distinction Not Enforced
- Concepts may get both Hebrew and Greek strongs
- No logic to prefer one based on OT/NT context

## Improving Coverage

To map more concepts:
1. Add stemming/lemmatization to match word variants
2. Use embedding similarity for semantic matching
3. Manual review of high-frequency unmatched concepts
4. Add synonym dictionaries

## Files

```
scripts/
├── extract_concepts.py   # Export concepts needing mapping
└── apply_strongs.py      # Apply mappings to database

.archive/                 # Previous attempt files (for reference)
```

## Database Schema

```sql
-- BibleVec.sqlite concepts table
CREATE TABLE concepts (
    id INTEGER PRIMARY KEY,
    stem TEXT,
    gloss TEXT,
    part_of_speech TEXT,  -- 'Verb' or 'Noun'
    strongs_mappings TEXT -- JSON array like '["G0025", "H0157"]'
);
```
