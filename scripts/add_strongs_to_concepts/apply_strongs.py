#!/usr/bin/env python3
"""
Apply strongs mappings from TSV to BibleVec.sqlite.
Input TSV format: id, stem, gloss, strongs_list (comma-separated)
"""

import sqlite3
import csv
import json
import argparse
from pathlib import Path

DB_PATH = '/workspace/databases/BibleVec.sqlite'


def main():
    parser = argparse.ArgumentParser(description='Apply strongs mappings to database')
    parser.add_argument('input', help='Input TSV with mappings (id, stem, gloss, strongs_list)')
    parser.add_argument('--db', default=DB_PATH, help='Path to BibleVec.sqlite')
    parser.add_argument('--clear-first', action='store_true', help='Clear all mappings before applying')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without changes')
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    cursor = conn.cursor()

    if args.clear_first and not args.dry_run:
        cursor.execute('UPDATE concepts SET strongs_mappings = NULL')
        print("Cleared all existing mappings")

    input_path = Path(args.input)
    with input_path.open('r') as f:
        reader = csv.DictReader(f, delimiter='\t')

        updated = 0
        skipped = 0

        for row in reader:
            cid = int(row['id'])
            strongs_str = row.get('strongs_list', '').strip()

            if not strongs_str:
                skipped += 1
                continue

            # Parse strongs list (comma-separated)
            strongs_list = [s.strip() for s in strongs_str.split(',') if s.strip()]

            if not strongs_list:
                skipped += 1
                continue

            strongs_json = json.dumps(strongs_list)

            if args.dry_run:
                print(f"Would update {cid}: {strongs_list}")
            else:
                cursor.execute(
                    'UPDATE concepts SET strongs_mappings = ? WHERE id = ?',
                    (strongs_json, cid)
                )
            updated += 1

    if not args.dry_run:
        conn.commit()

    conn.close()

    print(f"\nUpdated: {updated}")
    print(f"Skipped (no strongs): {skipped}")

    if args.dry_run:
        print("\n(Dry run - no changes made)")


if __name__ == '__main__':
    main()
