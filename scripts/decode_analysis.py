#!/usr/bin/env python3
"""
TBTA AnalyzedVerse Decoder

Parse TBTA AnalyzedVerse encoding from the verses/nodes database into structured JSON.
Useful for understanding the linguistic structure of Bible verses.

The AnalyzedVerse column contains TBTA's character-based linguistic encoding:
- Hierarchical structure: Clauses → Phrases → Words
- Position-based feature encoding
- Custom markup with ~\wd, ~\tg, ~\lu markers

Usage:
    # Parse a specific verse
    python scripts/decode_analysis.py "GEN 1:1" --pretty
    
    # Parse from database
    python scripts/decode_analysis.py "JHN 3:16" --database databases/verses.sqlite
    
    # Output to file
    python scripts/decode_analysis.py "MAT 5:3" --output verse.json
"""

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPT_DIR.parent
DB_DIR = PROJECT_DIR / "databases"

# Part type mappings
PART_TYPES = {
    'c': 'Clause',
    'n': 'NP',       # Noun Phrase
    'v': 'VP',       # Verb Phrase
    'j': 'AdjP',     # Adjective Phrase
    'a': 'AdvP',     # Adverb Phrase
    'N': 'Noun',
    'V': 'Verb',
    'A': 'Adjective',
    'D': 'Adverb',
    'P': 'Adposition',
    'C': 'Conjunction',
    'X': 'Particle',
    '.': 'Period',
    ' ': 'Space',
}

# Clause type codes
CLAUSE_TYPES = {
    'ID': 'Independent',
    'DP': 'Dependent',
    'PT': 'Patient (Object Complement)',
    'RL': 'Relative',
}

# Illocutionary force codes
ILLOCUTIONARY_FORCE = {
    'p': 'Declarative',
    'q': 'Interrogative',
    'i': 'Imperative',
    'j': 'Jussive',
    'o': 'Optative',
    'h': 'Hortatory',
}

# Number system
NUMBER_SYSTEM = {
    'S': 'Singular',
    'D': 'Dual',
    'T': 'Trial',
    'P': 'Plural',
    'p': 'Paucal',
    'Q': 'Quadral',
}

# Person system
PERSON_SYSTEM = {
    '1': 'First',
    '2': 'Second',
    '3': 'Third',
    'A': 'First Inclusive',
    'B': 'First Exclusive',
}

# Participant tracking
PARTICIPANT_TRACKING = {
    'I': 'First Mention',
    'D': 'Routine',
    'R': 'Restaging',
    'E': 'Exiting',
    'F': 'Frame Inferable',
    'G': 'Generic',
    'i': 'Interrogative',
}

# Semantic role
SEMANTIC_ROLE = {
    'A': 'Most Agent-like',
    'P': 'Most Patient-like',
    'N': 'Not Applicable',
}


class TBTAParser:
    """Parser for TBTA AnalyzedVerse encoding."""
    
    def __init__(self):
        self.tokens = []
        self.position = 0
    
    def parse(self, analyzed_verse: str) -> List[Dict[str, Any]]:
        """Parse an AnalyzedVerse string into structured JSON."""
        if not analyzed_verse or analyzed_verse.strip() == '':
            return []
        
        self.tokens = self._tokenize(analyzed_verse)
        self.position = 0
        
        clauses = []
        while self.position < len(self.tokens):
            clause = self._parse_clause()
            if clause:
                clauses.append(clause)
            else:
                self.position += 1
        
        return clauses
    
    def _tokenize(self, text: str) -> List[tuple]:
        """Tokenize AnalyzedVerse into (type, value) pairs."""
        tokens = []
        parts = text.split('~\\wd')
        
        for part in parts:
            if not part.strip():
                continue
            
            tag_match = re.search(r'~\\tg\s+([^\s~]+)', part)
            lu_match = re.search(r'~\\lu\s+([^~]*)', part)
            
            tag = tag_match.group(1) if tag_match else ''
            constituent = lu_match.group(1).strip() if lu_match else ''
            
            if tag or constituent:
                tokens.append(('element', {'tag': tag, 'constituent': constituent}))
        
        return tokens
    
    def _parse_clause(self) -> Optional[Dict[str, Any]]:
        """Parse a single clause."""
        if self.position >= len(self.tokens):
            return None
        
        token_type, token_data = self.tokens[self.position]
        tag = token_data.get('tag', '')
        constituent = token_data.get('constituent', '')
        
        if not tag.startswith('c-'):
            return None
        
        self.position += 1
        
        clause_info = self._decode_clause(tag)
        clause_info['Part'] = 'Clause'
        
        if constituent == '{':
            children = []
            while self.position < len(self.tokens):
                _, child_data = self.tokens[self.position]
                if child_data.get('constituent') == '}':
                    self.position += 1
                    break
                
                child = self._parse_element()
                if child:
                    children.append(child)
            
            if children:
                clause_info['Children'] = children
        
        return clause_info
    
    def _parse_element(self) -> Optional[Dict[str, Any]]:
        """Parse a phrase or word element."""
        if self.position >= len(self.tokens):
            return None
        
        token_type, token_data = self.tokens[self.position]
        tag = token_data.get('tag', '')
        constituent = token_data.get('constituent', '')
        
        if tag.startswith('.'):
            self.position += 1
            return {'Part': 'Period', 'Constituent': constituent or '.'}
        
        if not tag or tag == ' ':
            self.position += 1
            return None
        
        if tag and len(tag) > 0:
            part_code = tag[0]
            is_phrase = part_code.islower()
            
            if is_phrase:
                return self._parse_phrase()
            else:
                return self._parse_word()
        
        self.position += 1
        return None
    
    def _parse_phrase(self) -> Optional[Dict[str, Any]]:
        """Parse a phrase (NP, VP, AdjP, AdvP)."""
        if self.position >= len(self.tokens):
            return None
        
        token_type, token_data = self.tokens[self.position]
        tag = token_data.get('tag', '')
        constituent = token_data.get('constituent', '')
        
        self.position += 1
        
        phrase_info = self._decode_phrase(tag)
        
        if constituent == '(':
            children = []
            while self.position < len(self.tokens):
                _, child_data = self.tokens[self.position]
                if child_data.get('constituent') == ')':
                    self.position += 1
                    break
                
                child = self._parse_element()
                if child:
                    children.append(child)
            
            if children:
                phrase_info['Children'] = children
        
        return phrase_info
    
    def _parse_word(self) -> Optional[Dict[str, Any]]:
        """Parse a word element."""
        if self.position >= len(self.tokens):
            return None
        
        token_type, token_data = self.tokens[self.position]
        tag = token_data.get('tag', '')
        constituent = token_data.get('constituent', '')
        
        self.position += 1
        
        word_info = self._decode_word(tag)
        word_info['Constituent'] = constituent
        
        return word_info
    
    def _decode_clause(self, code: str) -> Dict[str, Any]:
        """Decode clause feature code."""
        result = {'Code': code}
        
        if len(code) >= 4:
            clause_type = code[2:4]
            result['Type'] = CLAUSE_TYPES.get(clause_type, clause_type)
        
        if len(code) >= 5:
            force = code[4]
            if force in ILLOCUTIONARY_FORCE:
                result['Illocutionary Force'] = ILLOCUTIONARY_FORCE[force]
        
        return result
    
    def _decode_phrase(self, code: str) -> Dict[str, Any]:
        """Decode phrase feature code."""
        result = {'Code': code}
        
        if len(code) >= 1:
            part = code[0]
            result['Part'] = PART_TYPES.get(part, part)
        
        if len(code) >= 4:
            role = code[3]
            if role in SEMANTIC_ROLE:
                result['Semantic Role'] = SEMANTIC_ROLE[role]
        
        return result
    
    def _decode_word(self, code: str) -> Dict[str, Any]:
        """Decode word feature code."""
        result = {'Code': code}
        
        if len(code) >= 1:
            part = code[0]
            result['Part'] = PART_TYPES.get(part, part)
        
        if part == 'N' and len(code) >= 10:
            result.update(self._decode_noun(code))
        elif part == 'V' and len(code) >= 10:
            result.update(self._decode_verb(code))
        elif part == 'A':
            result.update(self._decode_adjective(code))
        elif part == 'C':
            result['Part'] = 'Conjunction'
        elif part == 'P':
            result['Part'] = 'Adposition'
        
        return result
    
    def _decode_noun(self, code: str) -> Dict[str, Any]:
        """Decode noun feature positions."""
        result = {}
        
        if len(code) >= 3 and code[2] in NUMBER_SYSTEM:
            result['Number'] = NUMBER_SYSTEM[code[2]]
        
        if len(code) >= 6 and code[5] in PARTICIPANT_TRACKING:
            result['Participant Tracking'] = PARTICIPANT_TRACKING[code[5]]
        
        if len(code) >= 11 and code[10] in PERSON_SYSTEM:
            result['Person'] = PERSON_SYSTEM[code[10]]
        
        if len(code) >= 5:
            idx = code[4]
            if idx not in ['.', 'N']:
                result['NounListIndex'] = idx
        
        return result
    
    def _decode_verb(self, code: str) -> Dict[str, Any]:
        """Decode verb feature positions."""
        result = {}
        
        if len(code) >= 5:
            aspect = code[4]
            aspect_map = {
                'I': 'Imperfective',
                'C': 'Completive',
                'r': 'Inceptive',
                'U': 'Unmarked',
            }
            if aspect in aspect_map:
                result['Aspect'] = aspect_map[aspect]
        
        if len(code) >= 6:
            mood = code[5]
            if mood == 'I':
                result['Mood'] = 'Indicative'
        
        if len(code) >= 7:
            pol = code[6]
            if pol == 'N':
                result['Polarity'] = 'Negative'
            elif pol == 'A':
                result['Polarity'] = 'Affirmative'
        
        return result
    
    def _decode_adjective(self, code: str) -> Dict[str, Any]:
        """Decode adjective feature positions."""
        result = {}
        
        if len(code) >= 4:
            degree = code[3]
            degree_map = {
                'N': 'No Degree',
                'C': 'Comparative',
                'S': 'Superlative',
                'I': 'Intensified',
            }
            if degree in degree_map:
                result['Degree'] = degree_map[degree]
        
        return result


def parse_reference(reference: str) -> tuple:
    """Parse verse reference like 'GEN 1:1' or 'GEN.1.1'."""
    ref = reference.replace(':', '.').replace(' ', '.')
    parts = ref.split('.')
    
    if len(parts) != 3:
        raise ValueError(f"Invalid reference format: {reference}")
    
    book = parts[0].upper()
    chapter = int(parts[1])
    verse = int(parts[2])
    
    return book, chapter, verse


def get_verse_from_db(book: str, chapter: int, verse: int, db_path: Path) -> Optional[Dict]:
    """Get verse data from database."""
    if not db_path.exists():
        return None
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Try verses.sqlite format
    try:
        cursor.execute("""
            SELECT book, chapter, verse, verse_text, node_ids
            FROM verses
            WHERE book = ? AND chapter = ? AND verse = ?
        """, (book, chapter, verse))
        row = cursor.fetchone()
        if row:
            conn.close()
            return {
                'book': row[0],
                'chapter': row[1],
                'verse': row[2],
                'text': row[3],
                'node_ids': json.loads(row[4]) if row[4] else []
            }
    except sqlite3.OperationalError:
        pass
    
    # Try Bible_unified.sqlite format
    try:
        cursor.execute("""
            SELECT Book, USFM3, ChapterNum, VerseNum, Verse, AnalyzedVerse
            FROM verses
            WHERE USFM3 = ? AND ChapterNum = ? AND VerseNum = ?
        """, (book, chapter, verse))
        row = cursor.fetchone()
        if row:
            conn.close()
            return {
                'book_name': row[0],
                'book': row[1],
                'chapter': row[2],
                'verse': row[3],
                'text': row[4],
                'analyzed_verse': row[5]
            }
    except sqlite3.OperationalError:
        pass
    
    conn.close()
    return None


def get_nodes_from_db(node_ids: List[int], nodes_db: Path) -> List[Dict]:
    """Get node data from nodes.sqlite."""
    if not node_ids or not nodes_db.exists():
        return []
    
    conn = sqlite3.connect(nodes_db)
    cursor = conn.cursor()
    
    placeholders = ",".join("?" * len(node_ids))
    cursor.execute(f"""
        SELECT node_id, category, content, stem, sense, part_of_speech, feature_codes, concept_id
        FROM nodes
        WHERE node_id IN ({placeholders})
    """, node_ids)
    
    nodes = []
    for row in cursor.fetchall():
        nodes.append({
            'node_id': row[0],
            'category': row[1],
            'content': row[2],
            'stem': row[3],
            'sense': row[4],
            'part_of_speech': row[5],
            'feature_codes': row[6],
            'concept_id': row[7]
        })
    
    conn.close()
    return nodes


def main():
    parser = argparse.ArgumentParser(
        description='Decode TBTA AnalyzedVerse encoding to JSON'
    )
    parser.add_argument('reference', help='Verse reference (e.g., GEN.1.1 or "GEN 1:1")')
    parser.add_argument('--database', '-d', type=Path, help='Path to database')
    parser.add_argument('--output', '-o', help='Output JSON file (default: stdout)')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON')
    parser.add_argument('--raw', action='store_true', help='Show raw AnalyzedVerse')
    
    args = parser.parse_args()
    
    # Parse reference
    try:
        book, chapter, verse = parse_reference(args.reference)
    except ValueError as e:
        print(f"Error: {e}")
        print("Expected: BOOK.CHAPTER.VERSE (e.g., GEN.1.1)")
        return 1
    
    # Determine database path
    db_path = args.database
    if not db_path:
        # Try default locations
        for candidate in [
            DB_DIR / "verses.sqlite",
            PROJECT_DIR.parent / "mybibletoolbox-code" / "databases" / "Bible_unified.sqlite",
        ]:
            if candidate.exists():
                db_path = candidate
                break
    
    if not db_path or not db_path.exists():
        print(f"Error: No database found. Specify with --database")
        return 1
    
    # Get verse data
    verse_data = get_verse_from_db(book, chapter, verse, db_path)
    
    if not verse_data:
        print(f"Error: Verse not found: {book} {chapter}:{verse}")
        return 1
    
    result = {
        'book': verse_data.get('book', book),
        'chapter': verse_data.get('chapter', chapter),
        'verse': verse_data.get('verse', verse),
        'text': verse_data.get('text', ''),
    }
    
    # Parse structure if we have AnalyzedVerse
    analyzed = verse_data.get('analyzed_verse', '')
    if analyzed:
        if args.raw:
            result['raw_analyzed_verse'] = analyzed
        
        tbta_parser = TBTAParser()
        result['structure'] = tbta_parser.parse(analyzed)
    
    # Get nodes if available
    node_ids = verse_data.get('node_ids', [])
    if node_ids:
        nodes_db = DB_DIR / "nodes.sqlite"
        nodes = get_nodes_from_db(node_ids, nodes_db)
        if nodes:
            result['nodes'] = nodes
    
    # Format output
    indent = 2 if args.pretty else None
    json_output = json.dumps(result, indent=indent, ensure_ascii=False)
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"Written to {args.output}")
    else:
        print(json_output)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

