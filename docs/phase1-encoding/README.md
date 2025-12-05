# Phase 1 Encoding (He1)

Phase 1 encoding converts NIV Bible text into He1 controlled natural language for semantic analysis.

## Quick Start

1. **Main prompt**: [`/prompts/predict-phase1/CODEX-PROMPT.md`](../../prompts/predict-phase1/CODEX-PROMPT.md)
2. **Orchestration**: [`/prompts/predict-phase1/SKILL.md`](../../prompts/predict-phase1/SKILL.md)
3. **Learning workflow**: [`/prompts/predict-phase1/LEARN.md`](../../prompts/predict-phase1/LEARN.md)
4. **Examples**: [`/prompts/predict-phase1/examples.md`](../../prompts/predict-phase1/examples.md)

## Key Concepts

### The 7 Transforms

Apply sequentially when encoding:

| # | Transform | Description |
|---|-----------|-------------|
| 1 | COREF | Coreference resolution (3P→noun, 1P/2P→`P(ref)`) |
| 2 | SEGMENT | One verb per clause, split on conjunctions |
| 3 | VOCAB | Vocabulary levels (L0-L1 direct, L2 pair, L3 alternate) |
| 4 | BRACKETS | Relative, purpose, temporal, condition clauses |
| 5 | QUOTES | Quote structure (`said, ["..."]`) |
| 6 | DEIXIS | Speaker/addressee marking, clusivity |
| 7 | MARKERS | Discourse connectors, implicit info |

### Vocabulary Levels

| Level | Action | Example |
|-------|--------|---------|
| L0-1 | Use directly | man, go, house |
| L2 | Pair: `simple/complex` | serve/worship |
| L3 | Alternate sentences | `(complex) X. (simple) Y.` |
| L4 | Proper nouns direct | Bethlehem, Paul |

### Common Patterns

| NIV | He1 |
|-----|-----|
| LORD (all caps) | Yahweh |
| LORD Almighty | Yahweh-Almighty |
| bless | do good things for |
| can X | is able [to X] |
| to V (purpose) | [in order to V] |

## Reference Documentation

Detailed specifications in [`reference/`](reference/):
- [`notation.md`](reference/notation.md) - Full He1 syntax specification (35KB)
- [`checklist.md`](reference/checklist.md) - Validation checklist (78KB)
- [`learnings.md`](reference/learnings.md) - Encoding patterns from experience

## Historical Versions

Previous prompt iterations in [`archive/`](archive/):
- SUBAGENT-SKILL versions (V1-V4)
- learnings versions (v1-v4)

## Linter Integration

The linter (`/scripts/lint_check.py`) validates encoding quality:
- Catches pronoun errors, vocabulary violations, bracket mismatches
- Run BEFORE finalizing encoding
- Fix ALL errors (severity 0) and warnings (severity 1)

## Related

- [../methodology/](../methodology/) - Feature development workflow
- [/learnings/](../../learnings/) - Cross-feature patterns
- [/research/](../../research/) - TBTA source documentation
