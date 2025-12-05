#!/usr/bin/env python3
"""
TBTA Linter Check - Extract actionable error information from linter results.

Usage:
    python lint_check.py input/FILE.txt          # Process existing file
    python lint_check.py --text "He1 text here"  # Check new text
    python lint_check.py --all                   # Process all input/*.txt
    python lint_check.py --serve                 # Run as API on localhost:5000
    python lint_check.py --serve --port 8080     # Custom port
"""

import json
import re
import sqlite3
import ssl
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional, Tuple

SCRIPT_DIR = Path(__file__).parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent.parent.parent
NIV_DB = WORKSPACE_ROOT / "tbta-ai-framework/databases/niv.sqlite"


def parse_reference(ref: str) -> Optional[Tuple[str, int, int, Optional[int]]]:
    """
    Parse verse reference to (book, chapter, verse_start, verse_end).

    Formats:
        "1JN-003-015" -> ("1JN", 3, 15, None)
        "RUT-002-001-005" -> ("RUT", 2, 1, 5)
        "1JN3-15" -> ("1JN", 3, 15, None)  # Short format
        "RUT2-1-5" -> ("RUT", 2, 1, 5)     # Short format
    """
    ref = ref.strip().upper()

    # Full format: RUT-002-001 or RUT-002-001-005
    if match := re.match(r'^([A-Z0-9]{3})-(\d{3})-(\d{3})(?:-(\d{3}))?$', ref):
        book, ch, vs_start, vs_end = match.groups()
        return (book, int(ch), int(vs_start), int(vs_end) if vs_end else None)

    # Short format: 1JN3-15 or RUT2-1-5
    if match := re.match(r'^([A-Z0-9]{3})(\d+)-(\d+)(?:-(\d+))?$', ref):
        book, ch, vs_start, vs_end = match.groups()
        return (book, int(ch), int(vs_start), int(vs_end) if vs_end else None)

    return None


def fetch_niv_verses(book: str, chapter: int, verse_start: int, verse_end: Optional[int] = None) -> Optional[str]:
    """Fetch NIV verse(s) text from database."""
    if not NIV_DB.exists():
        return None

    try:
        conn = sqlite3.connect(NIV_DB)
        cursor = conn.cursor()

        if verse_end:
            cursor.execute(
                "SELECT text FROM niv WHERE book = ? AND chapter = ? AND verse >= ? AND verse <= ? ORDER BY verse",
                (book, chapter, verse_start, verse_end)
            )
            rows = cursor.fetchall()
            conn.close()
            return ' '.join(row[0] for row in rows) if rows else None
        else:
            cursor.execute(
                "SELECT text FROM niv WHERE book = ? AND chapter = ? AND verse = ?",
                (book, chapter, verse_start)
            )
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
    except Exception:
        return None


def check_linter(text: str) -> dict:
    """Call the Tabitha linter API with SSL workaround."""
    url = f"https://editor.tabitha.bible/check?text={urllib.parse.quote(text)}"
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        with urllib.request.urlopen(url, timeout=30, context=ssl_context) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}


def extract_token_info(tokens: list, parent_clause: str = "") -> list[dict]:
    """Recursively extract token info including messages and lookup_results."""
    results = []

    for token in tokens:
        token_text = token.get('token', '')
        token_type = token.get('type', '')

        # Track clause context
        current_clause = parent_clause
        if token_type == 'Clause':
            # Build clause text from sub_tokens
            clause_words = []
            for st in token.get('sub_tokens', []):
                if st.get('token'):
                    clause_words.append(st['token'])
            current_clause = ' '.join(clause_words)

        # Extract this token's data
        if token.get('messages') or token.get('lookup_results'):
            info = {
                'token': token_text,
                'type': token_type,
                'clause': current_clause or parent_clause,
                'messages': token.get('messages', []),
                'lookup_results': token.get('lookup_results', []),
                'case_frame_status': None,
                'valid_senses': [],
                'invalid_senses': []
            }

            # Analyze lookup_results for sense info
            for lr in token.get('lookup_results', []):
                sense_info = {
                    'sense': lr.get('sense', ''),
                    'gloss': lr.get('gloss', ''),
                    'pos': lr.get('part_of_speech', ''),
                    'level': lr.get('level', ''),
                    'ontology_status': lr.get('ontology_status', '')
                }

                cf = lr.get('case_frame', {})
                cf_status = cf.get('status', '')

                if cf_status == 'valid':
                    info['valid_senses'].append(sense_info)
                elif cf_status in ('invalid', 'unchecked'):
                    sense_info['case_frame_status'] = cf_status
                    sense_info['missing_args'] = cf.get('missing_arguments', [])
                    sense_info['extra_args'] = cf.get('extra_arguments', {})
                    info['invalid_senses'].append(sense_info)

            results.append(info)

        # Recurse into sub_tokens
        if token.get('sub_tokens'):
            results.extend(extract_token_info(token['sub_tokens'], current_clause))

    return results


def generate_report(linter_data: dict, reference: str = "", input_text: str = "") -> str:
    """Generate actionable report for agent consumption."""
    lines = []

    lines.append(f"# Linter Report: {reference or 'Direct input'}")
    lines.append("")

    if input_text:
        lines.append(f"**Input:** {input_text}")
        lines.append("")

    status = linter_data.get('status', 'unknown')

    if 'error' in linter_data:
        lines.append(f"**API Error:** {linter_data['error']}")
        return '\n'.join(lines)

    # Extract all token info
    tokens = linter_data.get('tokens', [])
    token_infos = extract_token_info(tokens)

    # Separate by message type
    errors_by_word = defaultdict(list)
    warnings_by_word = defaultdict(list)
    word_senses = {}  # token -> sense info

    for info in token_infos:
        token = info['token']

        # Store sense info for words
        if info['valid_senses'] or info['invalid_senses']:
            word_senses[token] = {
                'valid': info['valid_senses'],
                'invalid': info['invalid_senses'],
                'clause': info['clause']
            }

        for msg in info['messages']:
            label = msg.get('label', '')
            entry = {
                'message': msg.get('message', ''),
                'rule': msg.get('rule_id', '').split(' - ')[-1] if ' - ' in msg.get('rule_id', '') else msg.get('rule_id', ''),
                'clause': info['clause']
            }

            if label == 'error':
                errors_by_word[token].append(entry)
            elif label == 'warning':
                warnings_by_word[token].append(entry)

    # Count
    error_count = sum(len(v) for v in errors_by_word.values())
    warning_count = sum(len(v) for v in warnings_by_word.values())

    lines.append(f"**Status:** {status.upper()} | {error_count} errors, {warning_count} warnings")
    lines.append("")

    if error_count == 0:
        lines.append("✓ No errors found!")
        return '\n'.join(lines)

    # ERRORS - Detailed and Actionable
    lines.append("## Errors to Fix")
    lines.append("")

    for token, errs in sorted(errors_by_word.items()):
        if not token:
            continue

        lines.append(f"### `{token}`")

        # List errors
        lines.append("**Errors:**")
        seen_messages = set()
        for e in errs:
            if e['message'] not in seen_messages:
                lines.append(f"  - {e['message']}")
                seen_messages.add(e['message'])

        # Show available senses if this word has sense issues
        if token in word_senses:
            senses = word_senses[token]

            if senses['valid']:
                lines.append("**Valid senses (can use):**")
                for s in senses['valid']:
                    lines.append(f"  - `{token}_{s['sense']}` (L{s['level']}): {s['gloss']}")

            if senses['invalid']:
                lines.append("**Invalid senses (current usage doesn't match):**")
                for s in senses['invalid']:
                    reason = ""
                    if s.get('missing_args'):
                        reason = f" [missing: {', '.join(s['missing_args'])}]"
                    elif s.get('extra_args'):
                        reason = f" [unexpected args]"
                    lines.append(f"  - `{token}_{s['sense']}`: {s['gloss']}{reason}")

        # Check for quote-related missing arguments
        needs_quote_bracket = False
        if token in word_senses:
            for s in word_senses[token].get('invalid', []):
                if 'patient_clause_quote_begin' in s.get('missing_args', []):
                    needs_quote_bracket = True
                    break

        # Add fix hints based on error type
        fix_added = set()
        for e in errs:
            rule = e['rule']
            if 'stand-alone pronouns' in rule and 'pronoun' not in fix_added:
                lines.append(f"**Fix:** Replace `{token}` with the referent noun, e.g., `{token}(Ruth)` or just `Ruth`")
                fix_added.add('pronoun')
            elif "whose" in rule.lower() and 'whose' not in fix_added:
                lines.append(f"**Fix:** Rewrite `X whose Y` → `X [who had Y]`")
                fix_added.add('whose')
            elif 'level 2/3' in rule and 'level' not in fix_added:
                lines.append(f"**Fix:** `{token}` is Longman Defining Vocabulary (LDV) level 2/3 (complex). Use pairing with a level 0/1 word: `[{token}_A/simple-word_B]`")
                fix_added.add('level')
            elif 'two verbs' in rule and 'verbs' not in fix_added:
                lines.append(f"**Fix:** Split into separate clauses or bracket the subordinate clause with `[...]`")
                fix_added.add('verbs')
            elif ('case frame' in rule.lower() or 'argument' in rule.lower()) and 'case' not in fix_added:
                if needs_quote_bracket:
                    lines.append(f"**Fix:** Bracket the quoted speech: `{token} [..., \"quote here\"]`")
                else:
                    lines.append(f"**Fix:** Append sense to word (e.g., `{token}_A`). Pick from valid senses above, or restructure sentence to provide missing arguments.")
                fix_added.add('case')
            elif 'bracket before' in rule.lower() and 'bracket' not in fix_added:
                lines.append(f"**Fix:** Add `[` before the subordinate/relative clause or quoted speech")
                fix_added.add('bracket')

        lines.append("")

    # WARNINGS - Condensed
    if warning_count > 0:
        lines.append("## Warnings")
        for token, warns in sorted(warnings_by_word.items()):
            if token:
                unique_warns = list(set(w['message'] for w in warns))
                lines.append(f"- `{token}`: {unique_warns[0]}")
        lines.append("")

    return '\n'.join(lines)


def parse_input_file(filepath: Path) -> tuple[str, dict, str]:
    """Parse an input .txt file to extract reference, linter JSON, and NIV text."""
    content = filepath.read_text()

    # Extract reference
    ref_match = re.search(r'^Reference:\s*(.+)$', content, re.MULTILINE)
    reference = ref_match.group(1) if ref_match else filepath.stem

    # Extract NIV text
    niv_match = re.search(r'NIV Text:\n(.+?)(?:\n\nLinter|\Z)', content, re.DOTALL)
    niv_text = niv_match.group(1).strip() if niv_match else ""

    # Extract JSON
    json_start = content.find('Linter Results:\n')
    if json_start == -1:
        return reference, {"error": "No linter results found"}, niv_text

    json_data = content[json_start + len('Linter Results:\n'):]
    try:
        linter_data = json.loads(json_data)
        return reference, linter_data, niv_text
    except json.JSONDecodeError as e:
        return reference, {"error": f"Invalid JSON: {e}"}, niv_text


class LintCheckHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the linter API."""

    def do_POST(self):
        """Handle POST /check with text in body."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        # Parse body - accept JSON {"text": "..."} or plain text
        try:
            data = json.loads(body)
            text = data.get('text', '')
        except json.JSONDecodeError:
            text = body  # Plain text

        if not text:
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "No text provided"}).encode())
            return

        # Get linter results and generate report
        linter_data = check_linter(text)
        report = generate_report(linter_data, "", text)

        # Return both raw data and report
        response = {
            "input": text,
            #"raw": linter_data,
            "report": report
        }

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response, indent=2).encode())

    def do_GET(self):
        """Handle GET requests - check text or reference via query param."""
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        text = params.get('text', [''])[0]
        reference = params.get('reference', [''])[0]

        # If reference provided, fetch NIV text
        if reference:
            parsed_ref = parse_reference(reference)
            if not parsed_ref:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": f"Invalid reference format: {reference}",
                    "hint": "Use format: 1JN3-15 or RUT-002-001-005"
                }).encode())
                return

            book, chapter, verse_start, verse_end = parsed_ref
            text = fetch_niv_verses(book, chapter, verse_start, verse_end)

            if not text:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": f"Verse not found: {reference}",
                    "parsed": {"book": book, "chapter": chapter, "verse": verse_start}
                }).encode())
                return

            # Format reference string for report
            if verse_end:
                ref_str = f"{book} {chapter}:{verse_start}-{verse_end}"
            else:
                ref_str = f"{book} {chapter}:{verse_start}"

            linter_data = check_linter(text)
            report = generate_report(linter_data, ref_str, text)

            response = {
                "reference": ref_str,
                "niv": text,
                "report": report
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())

        elif text:
            # Run linter check on provided text
            linter_data = check_linter(text)
            report = generate_report(linter_data, "", text)

            response = {
                "input": text,
                "report": report
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())

        else:
            # Show usage
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            usage = """TBTA Lint Check API

GET /check?reference={verse_ref}   - Fetch NIV and check
GET /check?text={urlencoded_text}  - Check provided text
POST /check  (body: {"text": "..."} or plain text)

Reference formats:
  1JN3-15       (short: book + chapter + verse)
  RUT2-1-5      (short range)
  RUT-002-001   (full format)

Examples:
  curl "http://localhost:5000/check?reference=1JN3-16"
  curl "http://localhost:5000/check?reference=RUT-002-001-005"
  curl "http://localhost:5000/check?text=The%20man%20went%20home."
"""
            self.wfile.write(usage.encode())

    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {args[0]}")


def run_server(port: int = 5000):
    """Run the linter check API server."""
    server = HTTPServer(('localhost', port), LintCheckHandler)
    print(f"Lint Check API running on http://localhost:{port}")
    print("POST text to /check to get linter report")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python lint_check.py input/FILE.txt          # Process existing file")
        print("  python lint_check.py --text 'Text here'      # Check new text")
        print("  python lint_check.py --all                   # Process all input/*.txt")
        print("  python lint_check.py --serve                 # Run API on localhost:5000")
        print("  python lint_check.py --serve --port 8080     # Custom port")
        sys.exit(1)

    arg = sys.argv[1]

    if arg == '--serve':
        port = 5000
        if '--port' in sys.argv:
            port_idx = sys.argv.index('--port')
            if port_idx + 1 < len(sys.argv):
                port = int(sys.argv[port_idx + 1])
        run_server(port)

    elif arg == '--all':
        input_dir = SCRIPT_DIR / 'input'
        files = sorted(input_dir.glob('*.txt'))

        for f in files:
            print(f"\n{'='*60}")
            ref, linter_data, niv_text = parse_input_file(f)
            report = generate_report(linter_data, ref, niv_text)
            print(report)

    elif arg == '--text':
        if len(sys.argv) < 3:
            print("ERROR: --text requires text argument")
            sys.exit(1)

        text = sys.argv[2]
        linter_data = check_linter(text)
        report = generate_report(linter_data, "", text)
        print(report)

    else:
        filepath = Path(arg)
        if not filepath.is_absolute():
            filepath = SCRIPT_DIR / arg

        if not filepath.exists():
            print(f"ERROR: File not found: {filepath}")
            sys.exit(1)

        ref, linter_data, niv_text = parse_input_file(filepath)
        report = generate_report(linter_data, ref, niv_text)
        print(report)


if __name__ == "__main__":
    main()
