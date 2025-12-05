# Getting Started with TBTA AI

Quick start guide for Bible translators using AI-assisted encoding.

## What You'll Learn

1. How He1 encoding works
2. How to encode a verse
3. How to validate your encoding
4. How to learn from mistakes

## Prerequisites

- Basic understanding of TBTA concepts
- Access to NIV Bible text
- Familiarity with Claude or similar AI assistant

## Step 1: Understanding He1 Encoding

He1 converts Bible text into controlled natural language. The goal is to remove ambiguity so TBTA can generate accurate translations.

### Example: Ruth 1:1

**NIV:**
> In the days when the judges ruled, there was a famine in the land.

**He1:**
> The judges ruled the people of Israel. And during that time there was a famine in the land.

Key changes:
- Split into two clauses (one verb each)
- "the land" left generic (TBTA knows the context)
- "during that time" uses temporal marker

## Step 2: The 7 Transforms

Apply these in order when encoding:

### 1. COREF - Resolve Pronouns
| NIV | He1 |
|-----|-----|
| He went | Jesus went |
| She said | Ruth said |
| They worshiped | The disciples worshiped |

Keep 1P/2P pronouns: I, we, you → P(speaker) or you(addressee)

### 2. SEGMENT - Split Clauses
One verb per clause. Split on conjunctions.

| NIV | He1 |
|-----|-----|
| Jesus went and healed | Jesus went to the town. And Jesus healed... |

### 3. VOCAB - Vocabulary Levels
| Level | Action | Example |
|-------|--------|---------|
| L0-1 | Use directly | man, go, house |
| L2 | Use pair | serve/worship |
| L3 | Split sentences | (complex) X. (simple) Y. |

### 4. BRACKETS - Subordinate Clauses
```
Relative: [who was from Moab]
Purpose: [in order to go]
Temporal: [when Jesus arrived]
Condition: [if you believe]
```

### 5. QUOTES - Quote Structure
```
Jesus said, ["Come follow P(Jesus)."]
```
Multi-sentence: close bracket after first sentence.

### 6. DEIXIS - Speaker Marking
```
P(Jesus) = speaker self-reference
you(disciples) = addressee
we(inclusive) vs we(exclusive)
```

### 7. MARKERS - Discourse
```
(title) Section heading
(implicit-info) Background information
(complex) Difficult concept follows
```

## Step 3: Encode a Verse

1. Read the NIV verse carefully
2. Apply transforms 1-7 in order
3. Check against checklist
4. Run linter validation

### Practice: John 3:16

**NIV:**
> For God so loved the world that he gave his one and only Son, that whoever believes in him shall not perish but have eternal life.

**Your encoding:** (try before looking below)

<details>
<summary>Example He1</summary>

```
God loved people in the world very much.
(result) God gave his only Son [to people in the world].
And [if a person believes in God's Son] that person will not perish/die.
(result) That person will have life [that lasts forever].
```

Notes:
- "world" → "people in the world" (clarify)
- "so...that" → cause/result pattern
- "whoever" → "if a person...that person"
- L2 pair: perish/die
- Relative clause: [that lasts forever]
</details>

## Step 4: Validate

### Use the Linter
```bash
python scripts/lint_check.py "your encoding here"
```

The linter catches:
- Unresolved pronouns (3P he/she/they)
- Vocabulary violations
- Bracket mismatches
- Quote structure errors

### Common Errors

| Error | Fix |
|-------|-----|
| "he went" | Replace with name: "Jesus went" |
| "worship" alone | Use L2 pair: "serve/worship" |
| Missing bracket | Check all `[` have matching `]` |

## Step 5: Learn from Mistakes

When the linter or review finds errors:

1. Note what went wrong
2. Check [learnings/](../../learnings/) for similar cases
3. Update your mental model
4. Try again

See [docs/phase1-encoding/reference/learnings.md](../phase1-encoding/reference/learnings.md) for collected patterns.

## Next Steps

- [Phase 1 Encoding Reference](../phase1-encoding/) - Full He1 specification
- [Methodology](../methodology/) - 6-stage workflow
- [Research Features](../../research/features/) - Linguistic feature documentation

## Getting Help

- Check [learnings/README.md](../../learnings/README.md) for common patterns
- Review example encodings in [prompts/predict-phase1/examples.md](../../prompts/predict-phase1/examples.md)
- Consult the 4-persona peer review process in [methodology/peer-review.md](../methodology/peer-review.md)
