# He1 Encoder (V4)

> NIV→He1 controlled natural language. Linter validates output.

## Also Read
| File | Purpose |
|------|---------|
| `learnings-v4.md` | V4-specific edge cases |

---

## ❌ Linter Failures (avoid)
| Pattern | Fix |
|---------|-----|
| `[that X...]` patient clause | Remove "that": `knew [X...]` |
| `went-up`, `stood-up` | Base form: `go-up`, `stand-up` |
| can/could | `is able [to...]` |
| going to | `will` |
| even/any/own | Omit or rephrase |
| `give Y X` | `give X to Y` |
| double negative | Positive: `all people` |
| participles/gerunds | Rewrite: `It is fun [that X teaches]` |

---

## Transforms (apply sequentially)

### 1. COREF (coreference resolution)
- 3P→noun: repeat name ("David...David...David's")
- 1P/2P→`P(ref)`: `I(Paul)`, `you(people)`, `we(Peter)_excl`
- Generic labels: `you(people)` not `you(disciples)`
- Possessive: `of I(Paul)` not `I(Paul)'s`

### 2. SEGMENT (clause segmentation)
- One verb per clause
- Conjunction→new sentence: "X and Y did Z"→"X did A. And Y did B."
- Aspect verbs (start/stop/finish/continue) = NOT separate clause

### 3. VOCAB (simplification)
| Level | Action | Example |
|-------|--------|---------|
| L0-1 | Use directly | man, go, house |
| L2 | Pair: `simple/complex` | serve/worship |
| L3 | Alternate | `(complex) X. (simple) Y.` |
| L4 | Proper nouns direct | Bethlehem, Paul |

Forbidden words: can, even, any, own, "going to"

### 4. BRACKETS (subordination)
- Relative: `[who/that...]` — use "that" for people
- Purpose: `[in order to...]`
- Temporal: `[when/after/before...]` — prefer "after" if sequential
- Condition: `[if...]`
- Patient clause: NO leading "that" — `knew [X was...]`

### 5. QUOTES
```
Single:   X said, ["sentence"]
Multi:    X said, ["S1."] X said, ["S2."]
Nested:   ["outer ['inner']"]
Command:  said, ["You(X) (imp) go"]
```

### 6. DEIXIS
- Speaker: `I(Name)`, `my(Name's)`
- Addressee: `you(people)`, `your(X's)`
- Group: `we(Peter)_incl` / `we(Peter)_excl`
- Prayer/wish: `I(X) pray [that Yahweh will...]`
- Command: `You(X) (imp) verb`

### 7. MARKERS
- Discourse: And/But/Then/So (omit at section start)
- Implicit He1: `<<info>>` regular, `<info>` necessary
- Section: `(title)`, `_paragraph`
- Passive: `by X _implicitActiveAgent`

---

## Quick Transforms
| NIV | He1 |
|-----|-----|
| X, Y's Z (apposition) | X [who was Y's Z] |
| X the Y-ite | X [who was from Y] |
| LORD | Yahweh |
| bless | do good things for |
| find favor in eyes | be kind to |
| was left with | lived with only |
| captain | leader of the ship |
| sailors | men [that worked on that ship] |
| containers/jars | containers |
| famine | many people did not have enough food |
| can X | is able [to X] |
| to V (purpose) | [in order to V] |
| numbers | digits (2 not two) |
| prostrate | moved X's face to the ground |
| homeland | the land [that X was born in] |

## Common L2 Pairs
```
serve/worship, gather/harvest, grain/barley, family/clan,
leader/elder, servant/worker, gift/memorial, dream/vision,
officer/centurion, words/message, kneel/bow, promise/swear
```

## Determiners
| Context | Use |
|---------|-----|
| First mention specific | A certain man |
| First mention general | a man, some men |
| Already mentioned | that man |
| Contrast/new | this man |
| Frame inferable | the king |
| Generic | no article |

---

## Linter Check
```
python lint_check.py --text "your He1 text"
```
Shows errors with **Fix** hints, word senses (`_A`, `_B`), LDV levels.
Max 3 iterations. Fix all blocking errors.

---

## Output Format
```
{BOOK} {ch}:{vs} — He1 (V4)

{encoded text}

Linter: {clean or errors}
Issues: {patterns not covered}
```
