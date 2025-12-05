#!/usr/bin/env python3
"""
Prepare verse data for TBTA Phase1 encoding.

Fetches NIV verse(s), runs linter check, retrieves reference solution from verses.sqlite,
and writes data to files for subagent consumption.

Usage:
    python prepare_verse.py "Ruth 4:1"        # Single verse
    python prepare_verse.py "Matthew 2:1-10"  # Verse range
    python prepare_verse.py "John 3"          # Entire chapter
    python prepare_verse.py MAT-002-001       # Single verse (USFM format)
    python prepare_verse.py MAT-002           # Entire chapter (USFM format)
"""

import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Optional, Tuple

from lint_check import check_linter, generate_report

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent.parent.parent
NIV_DB = WORKSPACE_ROOT / "tbta-ai-framework/databases/niv.sqlite"
VERSES_DB = WORKSPACE_ROOT / "tbta-ai-framework/databases/verses.sqlite"
NODES_DB = WORKSPACE_ROOT / "tbta-ai-framework/databases/nodes.sqlite"

# USFM3 book codes mapping
BOOK_CODES = {
    # Old Testament
    "gen": "GEN", "genesis": "GEN",
    "exo": "EXO", "exodus": "EXO",
    "lev": "LEV", "leviticus": "LEV",
    "num": "NUM", "numbers": "NUM",
    "deu": "DEU", "deuteronomy": "DEU",
    "jos": "JOS", "joshua": "JOS",
    "jdg": "JDG", "judges": "JDG",
    "rut": "RUT", "ruth": "RUT",
    "1sa": "1SA", "1 samuel": "1SA",
    "2sa": "2SA", "2 samuel": "2SA",
    "1ki": "1KI", "1 kings": "1KI",
    "2ki": "2KI", "2 kings": "2KI",
    "1ch": "1CH", "1 chronicles": "1CH",
    "2ch": "2CH", "2 chronicles": "2CH",
    "ezr": "EZR", "ezra": "EZR",
    "neh": "NEH", "nehemiah": "NEH",
    "est": "EST", "esther": "EST",
    "job": "JOB",
    "psa": "PSA", "psalm": "PSA", "psalms": "PSA",
    "pro": "PRO", "proverbs": "PRO",
    "ecc": "ECC", "ecclesiastes": "ECC",
    "sng": "SNG", "song": "SNG", "song of solomon": "SNG",
    "isa": "ISA", "isaiah": "ISA",
    "jer": "JER", "jeremiah": "JER",
    "lam": "LAM", "lamentations": "LAM",
    "ezk": "EZK", "ezekiel": "EZK",
    "dan": "DAN", "daniel": "DAN",
    "hos": "HOS", "hosea": "HOS",
    "jol": "JOL", "joel": "JOL",
    "amo": "AMO", "amos": "AMO",
    "oba": "OBA", "obadiah": "OBA",
    "jon": "JON", "jonah": "JON",
    "mic": "MIC", "micah": "MIC",
    "nam": "NAM", "nahum": "NAM",
    "hab": "HAB", "habakkuk": "HAB",
    "zep": "ZEP", "zephaniah": "ZEP",
    "hag": "HAG", "haggai": "HAG",
    "zec": "ZEC", "zechariah": "ZEC",
    "mal": "MAL", "malachi": "MAL",
    # New Testament
    "mat": "MAT", "matthew": "MAT",
    "mrk": "MRK", "mark": "MRK",
    "luk": "LUK", "luke": "LUK",
    "jhn": "JHN", "john": "JHN",
    "act": "ACT", "acts": "ACT",
    "rom": "ROM", "romans": "ROM",
    "1co": "1CO", "1 corinthians": "1CO",
    "2co": "2CO", "2 corinthians": "2CO",
    "gal": "GAL", "galatians": "GAL",
    "eph": "EPH", "ephesians": "EPH",
    "php": "PHP", "philippians": "PHP",
    "col": "COL", "colossians": "COL",
    "1th": "1TH", "1 thessalonians": "1TH",
    "2th": "2TH", "2 thessalonians": "2TH",
    "1ti": "1TI", "1 timothy": "1TI",
    "2ti": "2TI", "2 timothy": "2TI",
    "tit": "TIT", "titus": "TIT",
    "phm": "PHM", "philemon": "PHM",
    "heb": "HEB", "hebrews": "HEB",
    "jas": "JAS", "james": "JAS",
    "1pe": "1PE", "1 peter": "1PE",
    "2pe": "2PE", "2 peter": "2PE",
    "1jn": "1JN", "1 john": "1JN",
    "2jn": "2JN", "2 john": "2JN",
    "3jn": "3JN", "3 john": "3JN",
    "jud": "JUD", "jude": "JUD",
    "rev": "REV", "revelation": "REV",
}


def parse_verse_reference(ref: str) -> Optional[Tuple[str, int, Optional[int], Optional[int]]]:
    """
    Parse verse reference to (book, chapter, verse_start, verse_end).
    
    Examples:
        "Ruth 4:1" -> ("RUT", 4, 1, None)
        "Matthew 2:1-10" -> ("MAT", 2, 1, 10)
        "MAT-002-001" -> ("MAT", 2, 1, None)
        "John 3" -> ("JHN", 3, None, None)  # Entire chapter
        "MAT-002" -> ("MAT", 2, None, None)  # Entire chapter
    """
    ref = ref.strip()
    
    # Try MAT-002-001 format (specific verse)
    if match := re.match(r'^([A-Z0-9]{3})-(\d{3})-(\d{3})(?:-(\d{3}))?$', ref):
        book, ch, vs_start, vs_end = match.groups()
        return (book, int(ch), int(vs_start), int(vs_end) if vs_end else None)
    
    # Try MAT-002 format (entire chapter)
    if match := re.match(r'^([A-Z0-9]{3})-(\d{3})$', ref):
        book, ch = match.groups()
        return (book, int(ch), None, None)
    
    # Try "Matthew 2:1-10" format (verse range)
    if match := re.match(r'^([A-Za-z0-9\s]+)\s+(\d+):(\d+)(?:-(\d+))?$', ref):
        book_name, ch, vs_start, vs_end = match.groups()
        book_code = BOOK_CODES.get(book_name.lower().strip())
        if not book_code:
            return None
        return (book_code, int(ch), int(vs_start), int(vs_end) if vs_end else None)
    
    # Try "John 3" format (entire chapter)
    if match := re.match(r'^([A-Za-z0-9\s]+)\s+(\d+)$', ref):
        book_name, ch = match.groups()
        book_code = BOOK_CODES.get(book_name.lower().strip())
        if not book_code:
            return None
        return (book_code, int(ch), None, None)
    
    return None


def fetch_niv_verse(book: str, chapter: int, verse: int) -> Optional[str]:
    """Fetch NIV verse text from database."""
    if not NIV_DB.exists():
        print(f"ERROR: NIV database not found at {NIV_DB}")
        return None
    
    try:
        conn = sqlite3.connect(NIV_DB)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT text FROM niv WHERE book = ? AND chapter = ? AND verse = ?",
            (book, chapter, verse)
        )
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"ERROR fetching NIV verse: {e}")
        return None


def get_chapter_verses(book: str, chapter: int) -> list[int]:
    """Get all verse numbers for a given chapter."""
    if not NIV_DB.exists():
        print(f"ERROR: NIV database not found at {NIV_DB}")
        return []
    
    try:
        conn = sqlite3.connect(NIV_DB)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT verse FROM niv WHERE book = ? AND chapter = ? ORDER BY verse",
            (book, chapter)
        )
        verses = [row[0] for row in cursor.fetchall()]
        conn.close()
        return verses
    except Exception as e:
        print(f"ERROR fetching chapter verses: {e}")
        return []


def fetch_reference_solution(book: str, chapter: int, verse: int) -> Optional[dict]:
    """
    Fetch reference verse_text and concatenated node content from databases.
    
    Returns dict with:
        - verse_text: str
        - node_content: str (concatenated with spaces)
    """
    if not VERSES_DB.exists() or not NODES_DB.exists():
        print(f"ERROR: Database not found")
        print(f"  Verses: {VERSES_DB.exists()}")
        print(f"  Nodes: {NODES_DB.exists()}")
        return None
    
    try:
        # Connect to verses database
        verses_conn = sqlite3.connect(VERSES_DB)
        verses_conn.execute(f"ATTACH DATABASE '{NODES_DB}' AS n")
        cursor = verses_conn.cursor()
        
        # Query with JOIN to get verse_text and concatenated node content
        cursor.execute("""
            SELECT 
                v.verse_text,
                GROUP_CONCAT(n.nodes.content, ' ') as node_content
            FROM verses v
            JOIN json_each(v.node_ids) AS je
            JOIN n.nodes ON n.nodes.node_id = je.value
            WHERE v.book = ? AND v.chapter = ? AND v.verse = ?
            GROUP BY v.book, v.chapter, v.verse
        """, (book, chapter, verse))
        
        row = cursor.fetchone()
        verses_conn.close()
        
        if row:
            return {
                "verse_text": row[0],
                "node_content": row[1]
            }
        return None
    except Exception as e:
        print(f"ERROR fetching reference solution: {e}")
        import traceback
        traceback.print_exc()
        return None


def write_section_data(book: str, chapter: int, verses: list[int],
                       verse_data: list[dict], linter_results: dict,
                       output_dir: Path) -> Path:
    """Write section data (one or more verses) to file for subagent consumption."""
    if len(verses) == 1:
        filename = f"{book}-{chapter:03d}-{verses[0]:03d}.txt"
        ref_str = f"{book} {chapter}:{verses[0]}"
    else:
        filename = f"{book}-{chapter:03d}-{verses[0]:03d}-{verses[-1]:03d}.txt"
        ref_str = f"{book} {chapter}:{verses[0]}-{verses[-1]}"
    
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Reference: {ref_str}\n")
        f.write(f"Verses: {len(verses)}\n\n")
        f.write("NIV Text:\n")
        for vdata in verse_data:
            f.write(f"{vdata['niv_text']}\n")
        f.write("\nLinter Results:\n")
        f.write(json.dumps(linter_results, indent=2))
    
    return filepath


def write_section_secret(book: str, chapter: int, verses: list[int],
                         solutions: list[dict], output_dir: Path) -> Path:
    """Write reference solutions to .secret file."""
    if len(verses) == 1:
        filename = f"{book}-{chapter:03d}-{verses[0]:03d}.secret"
        ref_str = f"{book} {chapter}:{verses[0]}"
    else:
        filename = f"{book}-{chapter:03d}-{verses[0]:03d}-{verses[-1]:03d}.secret"
        ref_str = f"{book} {chapter}:{verses[0]}-{verses[-1]}"
    
    filepath = output_dir / filename
    
    # Concatenate all verse texts and node contents
    all_verse_texts = [sol['verse_text'] for sol in solutions]
    all_node_contents = [sol['node_content'] for sol in solutions]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"Reference: {ref_str}\n")
        f.write(f"Verses: {len(verses)}\n\n")
        
        # Combined section text
        f.write("=== FULL SECTION (CONCATENATED) ===\n\n")
        f.write("Verse Text (Full):\n")
        f.write(" ".join(all_verse_texts) + "\n\n")
        
        f.write("Node Content (Full):\n")
        f.write(" ".join(all_node_contents) + "\n")
        
        # Per-verse breakdown
        if len(verses) > 1:
            f.write("\n\n=== PER-VERSE BREAKDOWN ===\n")
            for i, verse_num in enumerate(verses):
                f.write(f"\n--- Verse {verse_num} ---\n")
                f.write(f"Verse Text: {solutions[i]['verse_text']}\n")
                f.write(f"Node Content: {solutions[i]['node_content']}\n")
    
    return filepath


def process_section(book: str, chapter: int, verses: list[int], output_dir: Path) -> bool:
    """Process a section (one or more verses) and write combined output files. Returns True on success."""
    if len(verses) == 1:
        ref_str = f"{book} {chapter}:{verses[0]}"
    else:
        ref_str = f"{book} {chapter}:{verses[0]}-{verses[-1]}"
    
    print(f"\n{'='*60}")
    print(f"Processing {ref_str} ({len(verses)} verse{'s' if len(verses) > 1 else ''})")
    print(f"{'='*60}")
    
    # Step 1: Fetch all NIV verses
    print(f"1. Fetching NIV verses from {NIV_DB.name}...")
    verse_data = []
    combined_niv_text = []
    
    for verse in verses:
        niv_text = fetch_niv_verse(book, chapter, verse)
        if not niv_text:
            print(f"   ERROR: Could not fetch verse {verse}")
            return False
        verse_data.append({'verse': verse, 'niv_text': niv_text})
        combined_niv_text.append(niv_text)
    
    combined_text = " ".join(combined_niv_text)
    print(f"   Fetched {len(verses)} verses ({len(combined_text)} chars)")
    
    # Step 2: Check linter on combined text
    print("2. Checking linter on combined text...")
    linter_results = check_linter(combined_text)
    if "error" in linter_results:
        print(f"   WARNING: {linter_results['error']}")
    else:
        error_count = sum(1 for token in linter_results.get('tokens', []) 
                         for msg in token.get('messages', []) 
                         if msg.get('label') == 'error')
        print(f"   Linter: {error_count} errors")
    
    # Step 3: Write section data file
    print("3. Writing section data file...")
    section_file = write_section_data(book, chapter, verses, verse_data, linter_results, output_dir)
    print(f"   Written: {section_file.relative_to(WORKSPACE_ROOT)}")
    
    # Step 4: Fetch reference solutions for all verses
    print("4. Fetching reference solutions from verses.sqlite + nodes.sqlite...")
    solutions = []
    for verse in verses:
        solution = fetch_reference_solution(book, chapter, verse)
        if not solution:
            print(f"   WARNING: Could not fetch solution for verse {verse}")
            solutions.append({'verse_text': 'N/A', 'node_content': 'N/A'})
        else:
            solutions.append(solution)
    
    print(f"   Fetched {len(solutions)} reference solutions")
    
    # Step 5: Write secret file
    print("5. Writing .secret file...")
    secret_file = write_section_secret(book, chapter, verses, solutions, output_dir)
    print(f"   Written: {secret_file.relative_to(WORKSPACE_ROOT)}")
    
    return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python prepare_verse.py <verse_reference>")
        print("Examples:")
        print("  python prepare_verse.py 'Ruth 4:1'")
        print("  python prepare_verse.py 'Matthew 2:1-10'")
        print("  python prepare_verse.py 'John 3'          # Entire chapter")
        print("  python prepare_verse.py MAT-002-001")
        print("  python prepare_verse.py MAT-002           # Entire chapter")
        sys.exit(1)
    
    verse_ref = sys.argv[1]
    output_dir = SCRIPT_DIR / "input"
    output_dir.mkdir(exist_ok=True)
    
    # Parse reference
    parsed = parse_verse_reference(verse_ref)
    if not parsed:
        print(f"ERROR: Could not parse verse reference: {verse_ref}")
        sys.exit(1)
    
    book, chapter, verse_start, verse_end = parsed
    
    # Determine which verses to process
    verses_to_process = []
    
    if verse_start is None:
        # Entire chapter
        print(f"Fetching all verses for {book} {chapter}...")
        verses_to_process = get_chapter_verses(book, chapter)
        if not verses_to_process:
            print(f"ERROR: No verses found for {book} {chapter}")
            sys.exit(1)
        print(f"Found {len(verses_to_process)} verses in chapter {chapter}")
    elif verse_end is not None:
        # Verse range
        verses_to_process = list(range(verse_start, verse_end + 1))
        print(f"Processing verses {verse_start}-{verse_end} ({len(verses_to_process)} verses)")
    else:
        # Single verse
        verses_to_process = [verse_start]
    
    # Process the entire section as one file
    success = process_section(book, chapter, verses_to_process, output_dir)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    if success:
        print(f"✓ Successfully processed {len(verses_to_process)} verse{'s' if len(verses_to_process) > 1 else ''}")
        print(f"✓ Created 2 files (1 input + 1 secret)")
    else:
        print(f"✗ Failed to process section")
    print(f"\nOutput directory: {output_dir.relative_to(WORKSPACE_ROOT)}")
    print("\nDone! Files ready for subagent consumption.")


if __name__ == "__main__":
    main()

