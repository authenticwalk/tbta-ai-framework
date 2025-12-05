# TBTA Phase 1 (He1) — Orchestrator Skill

> **Mission**: Run parallel subagents to encode NIV verses to He1 (phase1), select best result, debug failures.

Phase1(He1) is a simplified english as a intermediary transcript to translate to all other languages

## Constants

$SUBAGENT_MODEL = 'haiku'

## Input Handling

**Required**: Verse reference — any format: `Ruth 4:1`, `RUT 4:1`, `Ruth 4:1-5`, `Matthew 2:1-10`
**Optional**: Verse text — if not provided, will be fetched
**Optional**: $SUBAGENT_SUBDIR - when provided pass this on the subagent, this puts them in debug mode and they log their results to that folder

| Input | Action |
|-------|--------|
| Reference + text | Use provided text |
| Reference only | Fetch text from sources |
| No reference | Return error |

```
# Examples
Ruth 4:1  Boaz went up to the town gate...   # uses provided text
Matthew 2:1-10                                 # fetches text
```

---

## Data Files

**Section Input File** (`input/{BOOK}-{ch:03d}-{vs:03d}[-{vs_end:03d}].txt`) — For subagent encoding:
- Reference (e.g., "MAT 2:1-8")
- Verse count
- NIV Text (all verses combined with spaces)
- Linter Results (JSON validation of full section)

**Section Secret File** (`input/{BOOK}-{ch:03d}-{vs:03d}[-{vs_end:03d}].secret`) — For orchestrator validation:
- Reference and verse count
- **Full Section**: Concatenated verse_text and node_content
- **Per-Verse Breakdown**: Individual verse data (for multi-verse sections only)

**CRITICAL**: Never pass `.secret` files to subagents! They contain the answer.

---

## Workflow

```
INPUT: Verse reference (text optional)
    │
    ├──► Subagent V1 (Policy)
    ├──► Subagent V2 (Evidence)
    ├──► Subagent V3 (Blended)
    └──► Subagent V4 (Compressed)
           │
           ▼
    COMPARE & SELECT (match verse_text)
           │
           ▼
    DEBUG FAILURES (analyze what went wrong)
           │
           ▼
    UPDATE LEARNINGS (wrong version's learnings-{v}.md)
```

## Process

1. **Prepare verse data** → Run `prepare_verse.py` to fetch all required data
   ```bash
   python prepare_verse.py "Matthew 2:1-8"    # Range: MAT-002-001-008.txt + .secret
   python prepare_verse.py "John 3"           # Chapter: JHN-003-001-036.txt + .secret
   python prepare_verse.py "Ruth 4:1"         # Single: RUT-004-001.txt + .secret
   ```
   This creates **ONE file per section** in `./input/` (not per verse):
   - `.txt` → Combined NIV text (all verses) + linter results for full section
   - `.secret` → Full concatenated reference + per-verse breakdown

2. **Launch subagents** → Run V1, V2, V3, V4 in parallel (see prompt below) using the model $SUBAGENT_MODEL
   - Pass them the `.txt` filename (they will load it)
   - DO NOT pass them the `.secret` file

3. **Collect results** → Each returns: He1 encoding (linter-validated) + issues

4. **Compare & select** → Match against reference from `.secret` file
   - The `.secret` file contains:
     - **Full Section**: Concatenated verse_text and node_content for entire section
     - **Per-Verse Breakdown**: Individual verse_text and node_content (for multi-verse sections)

5. **Debug failures** → Analyze what went wrong, update learnings

---

## Subagent Prompt

**For V1/V2/V3/V4** — adjust file names accordingly:
```
Read:
  - ./SUBAGENT-SKILL{-V2|-V3|-V4}.md
  - learnings-v{1|2|3|4}.md
  - ./input/{BOOK}-{ch:03d}-{vs:03d}.txt  (NIV + linter results)

Task: Encode the NIV verse to He1 (Phase 1)
Pay Attention to the errors and suggestions in the linter results

File Output: "Write to `${OUTPUT}`" OR Don't save to files
Return: He1 encoding (linter-validated), issues
NOTE: Run linter until clean (max 3 iterations) BEFORE returning
```


| Version | Skill File | Learnings | Notes |
|---------|------------|-----------|-------|
| V1 | `SUBAGENT-SKILL.md` | `learnings-v1.md` | Policy-first |
| V2 | `SUBAGENT-SKILL-V2.md` | `learnings-v2.md` | Evidence-based |
| V3 | `SUBAGENT-SKILL-V3.md` | `learnings-v3.md` | Blended |
| V4 | `SUBAGENT-SKILL-V4.md` | `learnings-v4.md` | Compressed (~2k tokens) |

---

## Selection Criteria

**Primary**: Match reference `verse_text` from Sources API.

**Exception**: If difference exists in both `verse_text` AND `semantic_encoding`, consider it acceptable — Phase 2 doesn't fix Phase 1 errors (e.g., "two" vs "2").
 - you may not have semantic_encoding in the new db so here are the acceptable errors
 - if it returns a number like 2 instead of two that is correct

**Tiebreakers** (if all match reference equally):
1. Linter passes (zero errors)
2. Pronoun resolution complete
3. Prefer V4 > V3 > V2 > V1

---

## Learnings Update Protocol

**Key principle**: Update the version(s) that got it WRONG, not the one that got it right.
**Key principle**: Think generic, if your rule will only apply to one word or one verse your not thinking broad enough.  Use well known techniques in the linguistic community like simplify based on longmans dictionary.  You may use highly technical terms about grammer and linguistics to compress rules

| Scenario | Action |
|----------|--------|
| All match reference | No update needed |
| Some wrong, some right | Update WRONG version's `learnings-{v}.md` |
| All wrong, same mistake | Add to ALL learnings files |

### Debug Process

1. **Identify** — what's wrong vs. reference?
2. **Diagnose** — which rule/pattern was missed?
3. **Consider fixes** — missing pattern? rule misinterpretation? vocabulary?
4. **Update** the appropriate learnings file

### Learnings Format

**CRITICAL**: Learnings must be GENERIC patterns applicable to ANY verse.

```markdown
## {Generic Category}
- {pattern} → `{solution}` (Mt 2:1, Ac 10:3)
```

**Rules**:
1. **Headers = Generic categories** — "L2 Word Pairings", "Verb Case Frames", "Quote Structure" — NEVER verse-specific ("Matthew 2:1-10 Learnings")
2. **Verse refs = Suffix only** — Add `(Mt 2:1)` at END to show evidence, not as headers
3. **No metadata** — Never add "(V1 Winner)", error counts, iteration counts
4. **Merge into existing sections** — Find the right category, don't create new verse-specific sections

### Rule Aggregation

**Before adding**, check for similar rules → merge into existing section with combined refs.

```markdown
# BAD (verse-specific section):
## Matthew 2:1-10 Learnings
- "Magi" → "wise men"

# GOOD (merged into generic section):
## L2 Word Substitutions
- "Magi" → "wise men" (Mt 2:1)
- "centurion" → "officer/centurion" (Ac 10:1)
```

**Aggregate when**: Same category, same pattern, only specific word differs.
**Keep separate when**: Different logic or exception to pattern.

---

## APIs

| Tool | URL |
|------|-----|
| Linter | `https://editor.tabitha.bible/check?text={urlencoded}` |
| Sources | `https://sources.tabitha.bible/Bible/{Book}/{ch}/{vs}` (use `Accept: application/json`) |
