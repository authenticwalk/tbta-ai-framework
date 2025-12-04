#!/usr/bin/env python3
"""
TBTA Database Converter

Converts source databases (Bible.sqlite, Bible - NIV.sqlite, Ontology.sqlite)
into normalized, split databases for efficient querying and cross-database joins.

Input:
  - databases/original/Bible.sqlite (66 book tables with AnalyzedVerse)
  - databases/original/Bible - NIV.sqlite (NIV translations)
  - databases/original/Ontology.sqlite (concepts table)

Output:
  - databases/verses.sqlite (verses with node_ids)
  - databases/nodes.sqlite (normalized nodes with concept_id)
  - databases/niv.sqlite (NIV translations)
  - databases/concepts.sqlite (Ontology concepts)
  - databases/strongs.sqlite (Strong's lexicon - from YAML files)

Usage:
    python scripts/convert_db.py
    python scripts/convert_db.py --source-dir /path/to/databases
"""

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Book table name to USFM 3.0 mapping
BOOK_TO_USFM = {
    "Genesis": "GEN", "Exodus": "EXO", "Leviticus": "LEV", "Numbers": "NUM", "Deuteronomy": "DEU",
    "Joshua": "JOS", "Judges": "JDG", "Ruth": "RUT", "1_Samuel": "1SA", "2_Samuel": "2SA",
    "1_Kings": "1KI", "2_Kings": "2KI", "1_Chronicles": "1CH", "2_Chronicles": "2CH",
    "Ezra": "EZR", "Nehemiah": "NEH", "Esther": "EST", "Job": "JOB", "Psalms": "PSA",
    "Proverbs": "PRO", "Ecclesiastes": "ECC", "Song_of_Solomon": "SNG", "Isaiah": "ISA",
    "Jeremiah": "JER", "Lamentations": "LAM", "Ezekiel": "EZK", "Daniel": "DAN",
    "Hosea": "HOS", "Joel": "JOL", "Amos": "AMO", "Obadiah": "OBA", "Jonah": "JON",
    "Micah": "MIC", "Nahum": "NAM", "Habakkuk": "HAB", "Zephaniah": "ZEP",
    "Haggai": "HAG", "Zechariah": "ZEC", "Malachi": "MAL",
    "Matthew": "MAT", "Mark": "MRK", "Luke": "LUK", "John": "JHN", "Acts": "ACT",
    "Romans": "ROM", "1_Corinthians": "1CO", "2_Corinthians": "2CO", "Galatians": "GAL",
    "Ephesians": "EPH", "Philippians": "PHP", "Colossians": "COL",
    "1_Thessalonians": "1TH", "2_Thessalonians": "2TH",
    "1_Timothy": "1TI", "2_Timothy": "2TI", "Titus": "TIT", "Philemon": "PHM", "Hebrews": "HEB",
    "James": "JAS", "1_Peter": "1PE", "2_Peter": "2PE",
    "1_John": "1JN", "2_John": "2JN", "3_John": "3JN", "Jude": "JUD", "Revelation": "REV",
}


class Config:
    """Configuration for database paths."""
    def __init__(self, source_dir: Path, output_dir: Path):
        self.source_dir = source_dir
        self.output_dir = output_dir
        
        # Source databases
        self.bible_db = source_dir / "Bible.sqlite"
        self.niv_db = source_dir / "Bible - NIV.sqlite"
        self.ontology_db = source_dir / "Ontology.sqlite"
        
        # Try alternative ontology path
        if not self.ontology_db.exists():
            alt = source_dir / "Ontology-download.sqlite"
            if alt.exists():
                self.ontology_db = alt
        
        # Output databases
        self.verses_db = output_dir / "verses.sqlite"
        self.nodes_db = output_dir / "nodes.sqlite"
        self.niv_output_db = output_dir / "niv.sqlite"
        self.concepts_db = output_dir / "concepts.sqlite"
        self.strongs_db = output_dir / "strongs.sqlite"
        
        # External data paths (relative to project root)
        project_root = Path(__file__).parent.parent
        self.biblevec_db = project_root.parent / "databases" / "BibleVec.sqlite"
        self.strongs_mappings_tsv = project_root / "scripts" / "add_strongs_to_concepts" / "data" / "concept_strongs_mappings.tsv"


# ============================================================
# PARSING FUNCTIONS
# ============================================================

def parse_chapter_verse(reference: str) -> Tuple[Optional[int], Optional[int]]:
    """Extract chapter and verse numbers from reference string."""
    if not reference:
        return None, None
    match = re.search(r'(\d+):(\d+)', reference)
    return (int(match.group(1)), int(match.group(2))) if match else (None, None)


def infer_part_from_tag(tag: str) -> str:
    """Infer part of speech from TBTA tag."""
    if not tag:
        return ''
    first_char = tag[0].upper()
    mapping = {
        'N': 'Noun', 'V': 'Verb', 'A': 'Adjective', 'D': 'Adverb',
        'P': 'Adposition', 'C': 'Conjunction', 'R': 'Particle'
    }
    return mapping.get(first_char, '')


def parse_analyzed_verse(analyzed_verse: str) -> List[Dict]:
    """
    Parse TBTA AnalyzedVerse into nodes.
    
    Returns list of dicts with: category, content, stem, sense, part_of_speech, feature_codes
    """
    if not analyzed_verse:
        return []
    
    nodes = []
    word_sections = analyzed_verse.split('~\\wd')
    
    for section in word_sections:
        if not section.strip() or '~\\lu' not in section:
            continue
        
        # Extract tag and constituent
        tag_match = re.search(r'~\\tg\s+([^~]+?)~\\lu', section)
        constituent_match = re.search(r'~\\lu\s+([^~]+)', section)
        
        if not tag_match or not constituent_match:
            continue
        
        tag = tag_match.group(1).strip()
        constituent = constituent_match.group(1).strip().rstrip('()')
        
        # Skip structural markers and empty content
        if not constituent or constituent in {'{', '}', '(', ')', '[', ']', '|', '.', ',', ';', ':', '!', '?', '-'}:
            continue
        if constituent.startswith('-'):
            continue
        
        # Parse tag into components
        category = tag[0] if tag else None
        feature_codes = None
        
        if '-' in tag:
            parts = tag.split('-', 1)
            category = parts[0]
            feature_codes = parts[1] if len(parts) > 1 else None
        
        part_of_speech = infer_part_from_tag(tag)
        
        # Handle compound constituents (e.g., "make/Acreate")
        if '/' in constituent:
            words = constituent.split('/')
            for i, word in enumerate(words):
                sense = None
                stem = word
                
                # Extract sense letter from subsequent words
                if i > 0 and word and word[0].isupper() and len(word) > 1:
                    sense = word[0]
                    stem = word[1:]
                
                if stem:
                    nodes.append({
                        'category': category,
                        'content': stem,
                        'stem': stem.lower(),
                        'sense': sense,
                        'part_of_speech': part_of_speech,
                        'feature_codes': feature_codes,
                    })
        else:
            nodes.append({
                'category': category,
                'content': constituent,
                'stem': constituent.lower(),
                'sense': None,
                'part_of_speech': part_of_speech,
                'feature_codes': feature_codes,
            })
    
    return nodes


def match_node_to_concept(cursor: sqlite3.Cursor, stem: str, part_of_speech: str, sense: str = None) -> Optional[int]:
    """Match a node to a concept by stem, part_of_speech, and sense."""
    # Try exact match with sense first
    if sense:
        cursor.execute(
            "SELECT id FROM concepts WHERE stem = ? AND part_of_speech = ? AND sense = ?",
            (stem, part_of_speech, sense)
        )
        row = cursor.fetchone()
        if row:
            return row[0]
    
    # Try without sense
    cursor.execute(
        "SELECT id FROM concepts WHERE stem = ? AND part_of_speech = ?",
        (stem, part_of_speech)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    
    # Try case-insensitive
    cursor.execute(
        "SELECT id FROM concepts WHERE LOWER(stem) = LOWER(?) AND part_of_speech = ?",
        (stem, part_of_speech)
    )
    row = cursor.fetchone()
    if row:
        return row[0]
    
    # Try without part of speech
    cursor.execute(
        "SELECT id FROM concepts WHERE LOWER(stem) = LOWER(?)",
        (stem,)
    )
    row = cursor.fetchone()
    return row[0] if row else None


# ============================================================
# DATABASE CREATION FUNCTIONS
# ============================================================

def create_concepts_db(cfg: Config):
    """Create concepts.sqlite from Ontology database."""
    print("\n[1/5] Creating concepts.sqlite...")
    
    if not cfg.ontology_db.exists():
        print(f"  ⚠ Ontology database not found: {cfg.ontology_db}")
        return False
    
    if cfg.concepts_db.exists():
        cfg.concepts_db.unlink()
    
    # Connect to source and target
    src_conn = sqlite3.connect(cfg.ontology_db)
    tgt_conn = sqlite3.connect(cfg.concepts_db)
    
    src_cur = src_conn.cursor()
    tgt_cur = tgt_conn.cursor()
    
    # Create schema (id is not unique in Ontology - same stem can have multiple senses)
    tgt_cur.execute('''
        CREATE TABLE concepts (
            id INTEGER,
            stem TEXT,
            sense TEXT,
            part_of_speech TEXT,
            gloss TEXT,
            brief_gloss TEXT,
            occurrences INTEGER,
            categorization TEXT,
            curated_examples TEXT,
            level INTEGER,
            note TEXT,
            strongs_mappings JSON
        )
    ''')
    
    # Try to copy from Concepts table
    try:
        src_cur.execute('''
            SELECT id, stem, sense, part_of_speech, gloss, brief_gloss, 
                   occurrences, categorization, curated_examples, level, note
            FROM Concepts
        ''')
        rows = src_cur.fetchall()
        # Add NULL for strongs_mappings column
        rows_with_null = [row + (None,) for row in rows]
        tgt_cur.executemany('''
            INSERT INTO concepts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', rows_with_null)
        print(f"  ✓ Copied {len(rows):,} concepts")
    except sqlite3.OperationalError as e:
        print(f"  ⚠ Error reading Concepts table: {e}")
        src_conn.close()
        tgt_conn.close()
        return False
    
    # Create indexes
    tgt_cur.execute("CREATE INDEX idx_concept_stem ON concepts(stem)")
    tgt_cur.execute("CREATE INDEX idx_concept_pos ON concepts(part_of_speech)")
    tgt_cur.execute("CREATE INDEX idx_concept_stem_pos ON concepts(stem, part_of_speech)")
    
    tgt_conn.commit()
    src_conn.close()
    tgt_conn.close()
    
    return True


def apply_strongs_mappings(cfg: Config):
    """Apply strongs mappings from TSV to concepts.sqlite."""
    print("  Applying strongs mappings...")
    
    if not cfg.strongs_mappings_tsv.exists():
        print(f"  ⚠ Strongs mappings TSV not found: {cfg.strongs_mappings_tsv}")
        return False
    
    import csv
    
    conn = sqlite3.connect(cfg.concepts_db)
    cur = conn.cursor()
    
    updated = 0
    with open(cfg.strongs_mappings_tsv, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            cid = int(row['id'])
            strongs_str = row.get('strongs_list', '').strip()
            
            if not strongs_str:
                continue
            
            strongs_list = [s.strip() for s in strongs_str.split(',') if s.strip()]
            if not strongs_list:
                continue
            
            strongs_json = json.dumps(strongs_list)
            cur.execute(
                'UPDATE concepts SET strongs_mappings = ? WHERE id = ?',
                (strongs_json, cid)
            )
            updated += 1
    
    conn.commit()
    conn.close()
    
    print(f"  ✓ Applied strongs mappings to {updated:,} concepts")
    return True


def create_niv_db(cfg: Config):
    """Create niv.sqlite from Bible - NIV database."""
    print("\n[2/5] Creating niv.sqlite...")
    
    if not cfg.niv_db.exists():
        print(f"  ⚠ NIV database not found: {cfg.niv_db}")
        return False
    
    if cfg.niv_output_db.exists():
        cfg.niv_output_db.unlink()
    
    src_conn = sqlite3.connect(cfg.niv_db)
    tgt_conn = sqlite3.connect(cfg.niv_output_db)
    
    src_cur = src_conn.cursor()
    tgt_cur = tgt_conn.cursor()
    
    # Create schema
    tgt_cur.execute('''
        CREATE TABLE niv (
            reference TEXT PRIMARY KEY,
            book CHAR(3) NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            text TEXT
        )
    ''')
    tgt_cur.execute("CREATE INDEX idx_niv_book ON niv(book, chapter, verse)")
    
    # Get all book tables
    src_cur.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name != 'Version'
        ORDER BY name
    """)
    tables = [row[0] for row in src_cur.fetchall()]
    
    total = 0
    for table_name in tables:
        usfm_code = BOOK_TO_USFM.get(table_name)
        if not usfm_code:
            continue
        
        try:
            src_cur.execute(f"SELECT Reference, Verse FROM [{table_name}]")
            for reference, verse_text in src_cur.fetchall():
                chapter, verse = parse_chapter_verse(reference)
                if chapter and verse:
                    ref_id = f"{usfm_code}-{chapter:03d}-{verse:03d}"
                    tgt_cur.execute(
                        "INSERT OR IGNORE INTO niv VALUES (?, ?, ?, ?, ?)",
                        (ref_id, usfm_code, chapter, verse, verse_text)
                    )
                    total += 1
        except sqlite3.OperationalError:
            continue
    
    tgt_conn.commit()
    src_conn.close()
    tgt_conn.close()
    
    print(f"  ✓ Copied {total:,} NIV verses")
    return True


def create_nodes_and_verses_db(cfg: Config):
    """Create nodes.sqlite and verses.sqlite from Bible.sqlite."""
    print("\n[3/5] Creating nodes.sqlite and verses.sqlite...")
    
    if not cfg.bible_db.exists():
        print(f"  ✗ Bible database not found: {cfg.bible_db}")
        return False
    
    # Remove existing
    for db in [cfg.nodes_db, cfg.verses_db]:
        if db.exists():
            db.unlink()
    
    # Connect to source
    src_conn = sqlite3.connect(cfg.bible_db)
    src_cur = src_conn.cursor()
    
    # Connect to concepts for matching
    concepts_conn = None
    concepts_cur = None
    if cfg.concepts_db.exists():
        concepts_conn = sqlite3.connect(cfg.concepts_db)
        concepts_cur = concepts_conn.cursor()
    
    # Create target databases
    nodes_conn = sqlite3.connect(cfg.nodes_db)
    verses_conn = sqlite3.connect(cfg.verses_db)
    
    nodes_cur = nodes_conn.cursor()
    verses_cur = verses_conn.cursor()
    
    # Create schemas
    nodes_cur.execute('''
        CREATE TABLE nodes (
            node_id INTEGER PRIMARY KEY,
            category CHAR(1),
            content TEXT,
            stem TEXT,
            sense CHAR(1),
            part_of_speech TEXT,
            feature_codes TEXT,
            concept_id INTEGER
        )
    ''')
    
    verses_cur.execute('''
        CREATE TABLE verses (
            reference TEXT PRIMARY KEY,
            book CHAR(3) NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            verse_text TEXT,
            node_ids JSON NOT NULL
        )
    ''')
    verses_cur.execute("CREATE INDEX idx_verses_book ON verses(book, chapter, verse)")
    
    # Get all book tables
    src_cur.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name != 'Version'
        ORDER BY name
    """)
    tables = [row[0] for row in src_cur.fetchall()]
    
    total_verses = 0
    total_nodes = 0
    verses_with_analysis = 0
    
    for table_name in tables:
        usfm_code = BOOK_TO_USFM.get(table_name)
        if not usfm_code:
            continue
        
        try:
            src_cur.execute(f"SELECT Reference, Verse, AnalyzedVerse FROM [{table_name}]")
            rows = src_cur.fetchall()
        except sqlite3.OperationalError:
            continue
        
        for reference, verse_text, analyzed_verse in rows:
            chapter, verse_num = parse_chapter_verse(reference)
            if not chapter or not verse_num:
                continue
            
            total_verses += 1
            
            # Parse nodes from AnalyzedVerse
            node_ids = []
            if analyzed_verse:
                verses_with_analysis += 1
                parsed_nodes = parse_analyzed_verse(analyzed_verse)
                
                for node in parsed_nodes:
                    # Match to concept
                    concept_id = None
                    if concepts_cur and node['part_of_speech']:
                        concept_id = match_node_to_concept(
                            concepts_cur,
                            node['stem'],
                            node['part_of_speech'],
                            node['sense']
                        )
                    
                    # Insert node
                    nodes_cur.execute('''
                        INSERT INTO nodes (category, content, stem, sense, part_of_speech, feature_codes, concept_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        node['category'],
                        node['content'],
                        node['stem'],
                        node['sense'],
                        node['part_of_speech'],
                        node['feature_codes'],
                        concept_id
                    ))
                    node_ids.append(nodes_cur.lastrowid)
                    total_nodes += 1
            
            # Insert verse
            ref_id = f"{usfm_code}-{chapter:03d}-{verse_num:03d}"
            verses_cur.execute('''
                INSERT INTO verses (reference, book, chapter, verse, verse_text, node_ids)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (ref_id, usfm_code, chapter, verse_num, verse_text, json.dumps(node_ids)))
        
        # Progress
        print(f"  Processed {table_name}: {len(rows)} verses")
    
    # Create indexes
    nodes_cur.execute("CREATE INDEX idx_nodes_category ON nodes(category)")
    nodes_cur.execute("CREATE INDEX idx_nodes_stem ON nodes(stem)")
    nodes_cur.execute("CREATE INDEX idx_nodes_concept ON nodes(concept_id)")
    
    # Commit and close
    nodes_conn.commit()
    verses_conn.commit()
    
    nodes_conn.close()
    verses_conn.close()
    src_conn.close()
    if concepts_conn:
        concepts_conn.close()
    
    print(f"  ✓ Created {total_verses:,} verses ({verses_with_analysis:,} with AnalyzedVerse)")
    print(f"  ✓ Created {total_nodes:,} nodes")
    return True


def create_strongs_db(cfg: Config):
    """Copy strongs table from BibleVec.sqlite."""
    print("\n[4/5] Creating strongs.sqlite...")
    
    if not cfg.biblevec_db.exists():
        print(f"  ⚠ BibleVec database not found: {cfg.biblevec_db}")
        print("  Creating empty strongs table instead...")
        if cfg.strongs_db.exists():
            cfg.strongs_db.unlink()
        conn = sqlite3.connect(cfg.strongs_db)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE strongs (
                strongs_number TEXT PRIMARY KEY,
                language TEXT,
                lemma TEXT,
                definition TEXT,
                derivation TEXT
            )
        ''')
        conn.commit()
        conn.close()
        return True
    
    if cfg.strongs_db.exists():
        cfg.strongs_db.unlink()
    
    # Copy strongs table from BibleVec
    src_conn = sqlite3.connect(cfg.biblevec_db)
    tgt_conn = sqlite3.connect(cfg.strongs_db)
    
    src_cur = src_conn.cursor()
    tgt_cur = tgt_conn.cursor()
    
    # Get schema from source
    src_cur.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='strongs'")
    schema = src_cur.fetchone()
    if not schema:
        print("  ⚠ strongs table not found in BibleVec.sqlite")
        src_conn.close()
        tgt_conn.close()
        return False
    
    # Create table and copy data
    tgt_cur.execute(schema[0])
    
    src_cur.execute("SELECT * FROM strongs")
    rows = src_cur.fetchall()
    
    # Get column count from schema
    src_cur.execute("PRAGMA table_info(strongs)")
    col_count = len(src_cur.fetchall())
    placeholders = ",".join(["?"] * col_count)
    
    tgt_cur.executemany(f"INSERT INTO strongs VALUES ({placeholders})", rows)
    
    tgt_conn.commit()
    src_conn.close()
    tgt_conn.close()
    
    print(f"  ✓ Copied {len(rows):,} Strong's entries from BibleVec.sqlite")
    return True


def print_summary(cfg: Config):
    """Print summary of created databases."""
    print("\n" + "=" * 60)
    print("CONVERSION COMPLETE")
    print("=" * 60)
    
    databases = [
        ("concepts.sqlite", cfg.concepts_db),
        ("niv.sqlite", cfg.niv_output_db),
        ("verses.sqlite", cfg.verses_db),
        ("nodes.sqlite", cfg.nodes_db),
        ("strongs.sqlite", cfg.strongs_db),
    ]
    
    print("\nCreated databases:")
    for name, path in databases:
        if path.exists():
            size = path.stat().st_size / 1024 / 1024
            print(f"  {name}: {size:.1f} MB")
        else:
            print(f"  {name}: NOT CREATED")
    
    print("\nExample cross-database query:")
    print('''
    -- Attach databases
    ATTACH 'databases/nodes.sqlite' AS n;
    ATTACH 'databases/concepts.sqlite' AS c;
    ATTACH 'databases/niv.sqlite' AS niv;

    -- Get verse words with meanings
    SELECT 
        v.book, v.chapter, v.verse,
        niv.niv.text AS niv_text,
        n.nodes.content AS word,
        c.concepts.gloss AS meaning
    FROM verses v
    JOIN json_each(v.node_ids) AS je
    JOIN n.nodes ON n.nodes.node_id = je.value
    LEFT JOIN c.concepts ON c.concepts.id = n.nodes.concept_id
    LEFT JOIN niv.niv ON niv.niv.book = v.book 
        AND niv.niv.chapter = v.chapter 
        AND niv.niv.verse = v.verse
    WHERE v.book = 'GEN' AND v.chapter = 1 AND v.verse = 1;
    ''')


def main():
    """Main conversion process."""
    # Determine paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent
    default_source = project_dir / "databases" / "original"
    default_output = project_dir / "databases"
    
    parser = argparse.ArgumentParser(description="Convert TBTA databases")
    parser.add_argument("--source-dir", type=Path, default=default_source,
                        help="Directory containing source databases")
    parser.add_argument("--output-dir", type=Path, default=default_output,
                        help="Output directory for converted databases")
    args = parser.parse_args()
    
    # Create config
    cfg = Config(args.source_dir, args.output_dir)
    
    print("=" * 60)
    print("TBTA Database Converter")
    print("=" * 60)
    print(f"Source: {cfg.source_dir}")
    print(f"Output: {cfg.output_dir}")
    
    # Check source databases
    sources = [
        ("Bible.sqlite", cfg.bible_db),
        ("Bible - NIV.sqlite", cfg.niv_db),
        ("Ontology.sqlite", cfg.ontology_db),
    ]
    
    print("\nSource databases:")
    for name, path in sources:
        status = "✓" if path.exists() else "✗ NOT FOUND"
        print(f"  {name}: {status}")
    
    if not cfg.bible_db.exists():
        print("\n✗ Bible.sqlite is required. Aborting.")
        sys.exit(1)
    
    # Create output directory
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run conversions
    create_concepts_db(cfg)
    apply_strongs_mappings(cfg)
    create_niv_db(cfg)
    create_nodes_and_verses_db(cfg)
    create_strongs_db(cfg)
    
    # Summary
    print_summary(cfg)


if __name__ == "__main__":
    main()
