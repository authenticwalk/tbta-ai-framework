#!/usr/bin/env python3
"""
Export TBTA training data from Bible_unified.sqlite.

Usage:
    python export_data.py /path/to/Bible_unified.sqlite
    python export_data.py /path/to/Bible_unified.sqlite --output ./data
"""

import argparse
import json
import re
import sqlite3
from pathlib import Path

# Well-audited books from TBTA
TARGET_BOOKS = [
    'Genesis', 'Joshua', 'Ruth', '1_Samuel', '2_Samuel',
    'Nehemiah', 'Esther', 'Daniel', 'Jonah', 'Nahum',
    'Matthew', 'Mark', 'Acts', 'Titus', 'Philemon', '2_John'
]

# Holdout chapters (middle chapter per book, or verse-based for single-chapter)
HOLDOUT_CHAPTERS = {
    'Genesis': 25, 'Joshua': 12, 'Ruth': 2, '1_Samuel': 16, '2_Samuel': 12,
    'Nehemiah': 7, 'Esther': 5, 'Daniel': 6, 'Jonah': 2, 'Nahum': 2,
    'Matthew': 14, 'Mark': 8, 'Acts': 14, 'Titus': 2,
    'Philemon': None, '2_John': None,  # Single-chapter: use verse-based holdout
}

SYSTEM_PROMPT = """Generate the TBTA semantic encoding for this Bible verse.

Output the complete AnalyzedVerse format which uses inline tags:
- ~\\wd marks word boundaries
- ~\\tg marks grammar tags (morphology codes)  
- ~\\lu marks lexical units

Grammar codes encode: part of speech, number, case, person, aspect, mood, etc.
Output ONLY the encoding, no other text."""


def parse_tbta_tags(analyzed_verse: str) -> list[dict]:
    """Parse TBTA AnalyzedVerse into structured word list."""
    words = []
    
    # Pattern to match word entries: ~\wd followed by tag and lexical unit
    pattern = r'~\\wd\s*~\\tg([A-Z]-[^\s~]+)\s*~\\lu([^~]+)'
    
    for match in re.finditer(pattern, analyzed_verse):
        tag = match.group(1).strip()
        lexical_unit = match.group(2).strip()
        
        # Extract part of speech from tag (first letter after the initial code)
        pos_map = {'N': 'Noun', 'V': 'Verb', 'A': 'Adjective', 'D': 'Adverb',
                   'P': 'Adposition', 'C': 'Conjunction', 'X': 'Particle'}
        pos_code = tag[2] if len(tag) > 2 else ''
        part = pos_map.get(pos_code, 'Other')
        
        words.append({
            'constituent': lexical_unit,
            'part': part,
            'tag': tag,
        })
    
    return words


def format_reference(book: str, chapter: int, verse: int) -> str:
    """Format verse reference."""
    return f"{book.replace('_', ' ')} {chapter}:{verse}"


def create_openai_message(reference: str, content: str) -> dict:
    """Create OpenAI chat format."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": reference},
            {"role": "assistant", "content": content}
        ]
    }


def create_google_message(reference: str, content: str) -> dict:
    """Create Google Vertex AI format."""
    return {
        "systemInstruction": {
            "role": "system",
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": reference}]},
            {"role": "model", "parts": [{"text": content}]}
        ]
    }


def is_holdout(book: str, chapter: int, verse: int, max_verse: int) -> bool:
    """Determine if verse belongs to holdout set."""
    holdout_chapter = HOLDOUT_CHAPTERS.get(book)
    if holdout_chapter is not None:
        return chapter == holdout_chapter
    else:
        # Single-chapter book: hold out last 20%
        return verse > int(max_verse * 0.8)


def export_dataset(db_path: str, output_dir: str):
    """Export training data in OpenAI and Google formats."""
    db_path = Path(db_path)
    output_dir = Path(output_dir)
    
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    
    # Create output directories
    openai_dir = output_dir / "openai"
    google_dir = output_dir / "google"
    openai_dir.mkdir(parents=True, exist_ok=True)
    google_dir.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get max verse for single-chapter books
    max_verses = {}
    for book in ['Philemon', '2_John']:
        cursor.execute(
            "SELECT MAX(VerseNum) FROM verses WHERE Book = ? AND ChapterNum = 1",
            (book,)
        )
        result = cursor.fetchone()
        max_verses[book] = result[0] if result else 25
    
    # Query verses
    placeholders = ','.join('?' * len(TARGET_BOOKS))
    cursor.execute(f"""
        SELECT Book, ChapterNum, VerseNum, Verse, AnalyzedVerse
        FROM verses
        WHERE Book IN ({placeholders})
          AND Verse IS NOT NULL
          AND AnalyzedVerse IS NOT NULL
        ORDER BY Book, ChapterNum, VerseNum
    """, TARGET_BOOKS)
    
    train_data = []
    holdout_data = []
    
    for book, chapter, verse_num, tbta_verse, analyzed_verse in cursor.fetchall():
        if not tbta_verse or not analyzed_verse:
            continue
        
        reference = format_reference(book, chapter, verse_num)
        max_v = max_verses.get(book, 999)
        
        entry = (reference, analyzed_verse)
        if is_holdout(book, chapter, verse_num, max_v):
            holdout_data.append(entry)
        else:
            train_data.append(entry)
    
    conn.close()
    
    # Write OpenAI format
    with open(openai_dir / "train.jsonl", 'w') as f:
        for ref, content in train_data:
            f.write(json.dumps(create_openai_message(ref, content)) + '\n')
    
    with open(openai_dir / "holdout.jsonl", 'w') as f:
        for ref, content in holdout_data:
            f.write(json.dumps(create_openai_message(ref, content)) + '\n')
    
    # Write Google format
    with open(google_dir / "train.jsonl", 'w') as f:
        for ref, content in train_data:
            f.write(json.dumps(create_google_message(ref, content)) + '\n')
    
    with open(google_dir / "holdout.jsonl", 'w') as f:
        for ref, content in holdout_data:
            f.write(json.dumps(create_google_message(ref, content)) + '\n')
    
    print(f"Exported {len(train_data)} training, {len(holdout_data)} holdout examples")
    print(f"  OpenAI: {openai_dir}")
    print(f"  Google: {google_dir}")
    
    return output_dir


def main():
    parser = argparse.ArgumentParser(description="Export TBTA training data")
    parser.add_argument("database", help="Path to Bible_unified.sqlite")
    parser.add_argument("--output", "-o", default="./data", help="Output directory")
    args = parser.parse_args()
    
    export_dataset(args.database, args.output)


if __name__ == "__main__":
    main()

