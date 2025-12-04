#!/usr/bin/env python3
"""
Extract concepts from BibleVec.sqlite for strongs mapping.
Outputs a TSV file with concepts that need strongs mappings.
"""

import sqlite3
import csv
import re
import argparse
from pathlib import Path

DB_PATH = '/workspace/databases/BibleVec.sqlite'

def should_skip(stem: str, gloss: str) -> tuple[bool, str]:
    """Check if concept should be skipped (no strongs mapping needed)."""
    stem_lower = stem.lower()
    gloss_lower = gloss.lower()

    # Numbers and dates
    if re.match(r'^[\d.]+$', stem) or re.match(r'^\d+th$', stem):
        return True, 'number'
    if re.search(r'\d+(AD|BC|AM|PM)$', stem):
        return True, 'date'

    # Grammar markers (start with -)
    if stem.startswith('-'):
        return True, 'grammar_marker'

    # DELETE markers
    if gloss_lower.startswith('delete'):
        return True, 'delete_marker'

    # Inexplicable
    if '(inexplicable)' in gloss_lower:
        return True, 'inexplicable'

    # Conjunctions/particles
    if stem in ('and', 'or', 'but', 'for', 'so', 'if', 'then', 'that', 'the', 'a', 'an'):
        return True, 'particle'

    # Transliterations
    if 'transliteration' in gloss_lower or 'aramaic word' in gloss_lower:
        return True, 'transliteration'

    return False, ''


def main():
    parser = argparse.ArgumentParser(description='Extract concepts for strongs mapping')
    parser.add_argument('--output', '-o', default='concepts_to_map.tsv', help='Output TSV file')
    parser.add_argument('--db', default=DB_PATH, help='Path to BibleVec.sqlite')
    parser.add_argument('--include-skipped', action='store_true', help='Include skipped concepts')
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, stem, gloss, part_of_speech, strongs_mappings
        FROM concepts
        ORDER BY id
    ''')

    output_path = Path(args.output)
    with output_path.open('w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['id', 'stem', 'gloss', 'part_of_speech', 'current_strongs', 'skip_reason'])

        total = 0
        to_map = 0
        skipped = 0

        for row in cursor.fetchall():
            cid, stem, gloss, pos, current_strongs = row
            total += 1

            skip, reason = should_skip(stem, gloss)
            if skip:
                skipped += 1
                if args.include_skipped:
                    writer.writerow([cid, stem, gloss, pos, current_strongs or '', reason])
            else:
                to_map += 1
                writer.writerow([cid, stem, gloss, pos, current_strongs or '', ''])

    conn.close()

    print(f"Total concepts: {total}")
    print(f"To map: {to_map}")
    print(f"Skipped: {skipped}")
    print(f"Output: {output_path}")


if __name__ == '__main__':
    main()
