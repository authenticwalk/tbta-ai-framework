# He1 Encoding Learnings

Patterns discovered from encoding sessions. For the complete encoding prompt, see [`/prompts/predict-phase1/CODEX-PROMPT.md`](../../../prompts/predict-phase1/CODEX-PROMPT.md).

## Critical Patterns

### Verb Case Frames
- `write` needs patient: "write a letter" not "write"
- `believe/trust` needs patient clause, not intransitive
- `give` patient-first: "give X to Y" not "give Y X"
- `see` needs specific Patient argument structure
- `command` requires different-participant: `command [people to...]` not `[I to...]`

### Hyphenated Verbs
- **ALWAYS base form**: `pick-up`, `go-up`, `stand-up`
- **NEVER past tense**: ~~`picked-up`~~ ~~`went-up`~~
- But `sit down`, `stand up` are TWO words and DO inflect: `sat down`, `stood up`

### Quote Patterns
- Single: `X said, ["sentence"]`
- Multi-sentence: split into `said, ["S1."] said, ["S2."]`
- Nested: `["outer ['inner']"]`
- Long quotes cause bracket-matching errors

### Deixis
- Speaker: `I(Paul)`, `my(Paul's)` → prefer `of I(Paul)`
- Addressee: `you(people)`, `your(X's)`
- Group: `we(Peter)_incl` / `we(Peter)_excl`
- Generic labels: `you(people)` not `you(disciples)`
- Compound deixis NOT supported: `we(Paul-and-Timothy)` FAILS → use `we(people)`

### Determiners
| Context | Pattern |
|---------|---------|
| First mention specific | A certain man |
| First mention general | a man, some men |
| Already mentioned | that man |
| Contrast/new | this man |
| Frame inferable | the king |

### Patient Clauses
- NO leading "that": `knew [X was...]` not `knew [that X was...]`
- Patient must immediately follow verb

### Vocabulary (L2 Pairs)
```
serve/worship, gather/harvest, grain/barley, family/clan,
leader/elder, servant/worker, gift/memorial, dream/vision,
officer/centurion, words/message, kneel/bow, promise/swear,
representative/apostle, rescuer/savior, happy/blessed
```

### Forbidden Words
`can`, `even`, `any`, `own`, `going to`
- `can X` → `is able [to X]`
- `going to` → `will`

---

## Structural Patterns

### Narrative
- `(title)` at section starts (but OT uses `-Title X.`)
- "One day" opener for narrative beginnings
- "decided [to verb]" for intent

### Epistle
- Dense passages need aggressive segmentation
- `_paragraph` at section starts
- "(complex)/(simple)" for difficult concepts

### Prophetic/Poetic
- Double negative → positive: "will not leave unpunished" → "will certainly punish"
- Causative for nature: "dries up the sea" → "causes [the sea to become dry]"
- Simile: `[like X verb Y]`

---

## Deity Naming

| Context | Use |
|---------|-----|
| Genesis (Elohim) | God |
| LORD (all caps) | Yahweh |
| LORD Almighty | Yahweh-Almighty (hyphenated) |

---

## Common Expansions

| NIV | He1 |
|-----|-----|
| bless | do good things for |
| find favor in eyes | be kind to |
| famine | many people did not have enough food |
| captain | leader of the ship |
| sailors | men [who worked on that ship] |
| sackcloth | rough cloth |
| prostrate | moved X's face to the ground |
| homeland | the land [that X was born in] |
| called X (summon) | seek-attention X. and X give-attention to Y. |
| May the Lord... | I pray [that Yahweh will...] |

---

## Historical Versions

Detailed encoding session logs in `/prompts/predict-phase1/`:
- `learnings-v1.md` — Policy-First patterns
- `learnings-v2.md` — Evidence-Based patterns
- `learnings-v3.md` — Blended approach patterns
- `learnings-v4.md` — Latest compressed patterns
