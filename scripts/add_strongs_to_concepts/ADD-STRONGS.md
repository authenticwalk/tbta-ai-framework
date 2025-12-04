# Add Strong's Mappings to TBTA Concepts

Complete prompt for mapping TBTA concepts to Strong's numbers.

## Prerequisites

- `/workspace/databases/BibleVec.sqlite` with `concepts` and `strongs` tables
- Python 3 with sqlite3

## Task

Map TBTA semantic concepts to Strong's concordance numbers using definition text matching.

## Step 1: Extract Concepts

```bash
python3 plan/tbta-concept-strongs-mappings/scripts/extract_concepts.py \
    -o plan/tbta-concept-strongs-mappings/concepts_to_map.tsv
```

## Step 2: Run Mapping Script

Create and run a mapping script that:

```python
#!/usr/bin/env python3
"""Map concepts to strongs using definition matching."""
import sqlite3
import json
import re
import csv

DB_PATH = '/workspace/databases/BibleVec.sqlite'

def is_proper_name(defn):
    """Check if definition is for a proper name."""
    d = defn.lower()
    return any(x in d for x in [
        'a name', 'a place', 'an israelite', 'a region', 'a city',
        'a country', 'a tribe', 'a river', 'a mountain',
        'of uncertain derivation', 'of foreign origin'
    ])

def should_skip(stem, gloss):
    """Check if concept should skip mapping."""
    if re.match(r'^[\d.]+$', stem) or re.match(r'^\d+th$', stem):
        return True
    if re.search(r'\d+(AD|BC|AM|PM)$', stem):
        return True
    if stem.startswith('-'):
        return True
    if gloss.lower().startswith('delete'):
        return True
    if '(inexplicable)' in gloss.lower():
        return True
    if stem in ('and', 'or', 'but', 'for', 'so', 'if', 'then', 'that', 'the', 'a', 'an'):
        return True
    if 'transliteration' in gloss.lower():
        return True
    return False

def find_strongs(stem, pos, strongs_entries):
    """Find matching strongs for a concept."""
    stem_lower = stem.lower()
    results = []

    for snum, lemma, defn in strongs_entries:
        if not defn or is_proper_name(defn):
            continue

        defn_lower = defn.lower()

        # Priority 1: "to {stem}" for verbs
        if pos == 'Verb' and defn_lower.startswith(f'to {stem_lower}'):
            results.append((snum, 1))
            continue

        # Priority 2: "a/an {stem}" for nouns
        if pos == 'Noun' and re.match(rf'^(?:a|an) {re.escape(stem_lower)}\b', defn_lower):
            results.append((snum, 2))
            continue

        # Priority 3: starts with stem directly
        if defn_lower.startswith(stem_lower):
            results.append((snum, 3))
            continue

        # Priority 4: "to {stem}" anywhere
        if f'to {stem_lower}' in defn_lower:
            results.append((snum, 4))
            continue

        # Priority 5: stem as word boundary anywhere
        if re.search(rf'\b{re.escape(stem_lower)}\b', defn_lower):
            results.append((snum, 5))

    results.sort(key=lambda x: x[1])
    seen = set()
    unique = []
    for snum, _ in results:
        if snum not in seen:
            seen.add(snum)
            unique.append(snum)
    return unique[:5]

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Load strongs
    cur.execute('SELECT strongs_number, lemma, definition FROM strongs WHERE definition IS NOT NULL')
    strongs_entries = list(cur.fetchall())

    # Load concepts
    cur.execute('SELECT id, stem, gloss, part_of_speech FROM concepts ORDER BY id')
    concepts = list(cur.fetchall())

    # Map and update
    cur.execute('UPDATE concepts SET strongs_mappings = NULL')

    with open('concept_strongs_output.tsv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['id', 'stem', 'gloss', 'strongs_list'])

        matched = 0
        for cid, stem, gloss, pos in concepts:
            if should_skip(stem, gloss):
                writer.writerow([cid, stem, gloss, ''])
                continue

            strongs = find_strongs(stem, pos, strongs_entries)
            strongs_str = ','.join(strongs)
            writer.writerow([cid, stem, gloss, strongs_str])

            if strongs:
                matched += 1
                cur.execute(
                    'UPDATE concepts SET strongs_mappings = ? WHERE id = ?',
                    (json.dumps(strongs), cid)
                )

    conn.commit()
    print(f"Matched: {matched}/{len(concepts)}")
    conn.close()

if __name__ == '__main__':
    main()
```

Save as `run_mapping.py` and execute:

```bash
python3 run_mapping.py
```

## Step 3: Verify Results

```python
import sqlite3
import json

conn = sqlite3.connect('/workspace/databases/BibleVec.sqlite')
cur = conn.cursor()

# Count
cur.execute('SELECT COUNT(*) FROM concepts WHERE strongs_mappings IS NOT NULL')
print(f"With mappings: {cur.fetchone()[0]}")

# Sample verification
samples = ['abandon', 'love', 'king', 'save', 'God', 'forgive']
for stem in samples:
    cur.execute('''
        SELECT stem, strongs_mappings FROM concepts
        WHERE stem = ? AND strongs_mappings IS NOT NULL LIMIT 1
    ''', (stem,))
    row = cur.fetchone()
    if row:
        print(f"{row[0]}: {json.loads(row[1])}")
```

Expected output:
```
abandon: ['G2641', 'H3363']
love: ['G0025', 'H5690', 'H5691']
king: ['H4428', 'H4430']
save: ['G4982', 'G1295']
God: ['H0426']
forgive: ['H5545']
```

## Step 4: Export for Backup

```python
import sqlite3
import json

conn = sqlite3.connect('/workspace/databases/BibleVec.sqlite')
cur = conn.cursor()
cur.execute('SELECT id, strongs_mappings FROM concepts WHERE strongs_mappings IS NOT NULL')

rebuild_data = {row[0]: json.loads(row[1]) for row in cur.fetchall()}
with open('concept_strongs_rebuild.json', 'w') as f:
    json.dump(rebuild_data, f, indent=2)

print(f"Exported {len(rebuild_data)} mappings")
```

## Batch Processing (Optional)

For AI review of unmapped concepts, batch them:

```python
import sqlite3
import csv

conn = sqlite3.connect('/workspace/databases/BibleVec.sqlite')
cur = conn.cursor()

# Get unmapped concepts
cur.execute('''
    SELECT id, stem, gloss, part_of_speech FROM concepts
    WHERE strongs_mappings IS NULL
    ORDER BY id
''')

BATCH_SIZE = 100
batch_num = 0
rows = list(cur.fetchall())

for i in range(0, len(rows), BATCH_SIZE):
    batch = rows[i:i+BATCH_SIZE]
    batch_num += 1
    with open(f'batch_{batch_num:03d}.tsv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['id', 'stem', 'gloss', 'part_of_speech', 'suggested_strongs'])
        for row in batch:
            writer.writerow([*row, ''])

print(f"Created {batch_num} batches")
```

Then review each batch and add suggested strongs, then apply with:

```bash
python3 scripts/apply_strongs.py batch_001.tsv
```

## Cleanup

After successful mapping:

```bash
rm -f run_mapping.py concept_strongs_output.tsv batch_*.tsv
```

Keep `concept_strongs_rebuild.json` as backup.
