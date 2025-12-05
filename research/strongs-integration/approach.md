# TBTA Strong's Hints Approach

## Core Idea

Instead of annotating TBTA features verse-by-verse, annotate them **Strong's word-by-Strong's word** with translation hints based on cross-linguistic patterns.

### The Proposal

For each Strong's entry (~8,000 Greek/Hebrew words), add TBTA hints that encode patterns like:

```yaml
# Example: Strong's G846 (αὐτός - he/she/it/they)
strongs: G846
gloss: "he, she, it, they, same"
tbta_hints:
  person:
    - pattern: "when Japanese uses 彼ら (karera)"
      hint: "likely 3rd person plural, human"
    - pattern: "when Thai uses เขา (khao)"
      hint: "likely 3rd person singular"
    - pattern: "when Navajo uses different word than regular 3rd"
      hint: "likely 4th person (obviative)"

  number:
    - pattern: "when Samoan uses lāua (dual pronoun)"
      hint: "exactly 2 persons"
    - pattern: "when Hawaiian uses lākou (trial pronoun)"
      hint: "exactly 3 persons"

  surface_realization:
    default: "pronoun"
    note: "Pro-drop languages (Spanish, Japanese) may use zero"
```

### How It Works in Practice

**Step 1: Annotate Strong's Entries (One-Time)**
- Analyze how 900+ translations handle each Strong's word across all its occurrences
- Extract patterns: "Language X uses word Y in context Z → TBTA feature = value"
- Store hints on the Strong's entry

**Step 2: Use Hints for Translation (Per-Verse)**
- Load the verse to be translated
- Load all Strong's entries for words in that verse
- Strong's hints provide guidance based on proven translation patterns
- AI/translator makes final decision based on hints + context

### Key Advantages

1. **Reduced Annotation Workload**
   - ~8,000 Strong's entries vs ~31,000 verses
   - Patterns discovered once, applied many times

2. **Cross-Linguistic Wisdom**
   - Leverage existing translations as evidence
   - "Language family X consistently uses pattern Y for this word"

3. **Cumulative Learning**
   - Hints improve as more translations analyzed
   - Community contributions can refine hints

4. **Context-Aware When Needed**
   - Hints are suggestions, not rigid rules
   - Verse context overrides hints when appropriate

5. **Complementary to Macula**
   - Macula provides morphology/semantics
   - Strong's hints provide cross-linguistic translation patterns

### Example Scenario

**Translating Genesis 4:8 to Navajo (has 3rd vs 4th person distinction):**

```
Verse: "Cain said to Abel his brother, and he rose up and he killed him"
Problem: Which "he" is which? Navajo needs 3rd (subject) vs 4th (different subject)

Strong's Data Available:
- G846 (he) occurrence 1: hints suggest "subject continuation → 3rd person"
- G846 (he) occurrence 2: hints suggest "subject continuation → 3rd person"
- G846 (him) occurrence 3: hints suggest "object, different from subject → 4th person"

Plus Verse Context:
- NounListIndex: Cain=1, Abel=2
- Participant Tracking: Cain=routine subject, Abel=exiting

Combined Result:
- "he rose up" = 3rd person (Cain, subject continuation)
- "he killed" = 3rd person (Cain, still subject)
- "him" = 4th person (Abel, different from subject)
```

---

## Which TBTA Features Would Benefit?

### TIER 1: Strong Lexical Association (Hints are highly effective)

These features are inherent to the word itself and remain relatively stable across contexts:

| Feature | Strong's Benefit | Why It Works | Example |
|---------|-----------------|--------------|---------|
| **Number System** | ★★★★★ Excellent | Pronouns/nouns have inherent number; translations reveal it | G846 (αὐτός) → when Hawaiian uses lākou → trial (3 persons) |
| **Person System** | ★★★★★ Excellent | Pronouns encode person; clusivity visible in translations | G2249 (ἡμεῖς) → when Tagalog uses "kami" → exclusive, "tayo" → inclusive |
| **Proximity** | ★★★★★ Excellent | Demonstratives have spatial/temporal distance encoded | G3778 (οὗτος) → when Japanese uses これ → near speaker |
| **Polarity** | ★★★★☆ Very Good | Some words carry inherent negation | G3756 (οὐ) → always negative polarity |
| **Lexical Sense** | ★★★★★ Excellent | Polysemy is word-specific; translations disambiguate | G3056 (λόγος) → when used for "accounting" vs "speech" vs "Word of God" |
| **Surface Realization** | ★★★★☆ Very Good | Word class relatively stable | G1473 (ἐγώ) → defaults to pronoun, but pro-drop langs use zero |

**Implementation Pattern:**
```yaml
strongs: G2249
gloss: "we"
tbta_hints:
  person:
    baseline: "First person plural"
    clusivity_patterns:
      - context: "divine speech (Trinity addressing Trinity)"
        translations:
          - lang: "tgl"  # Tagalog
            word: "kami"
            hint: "exclusive (Trinity members only)"
      - context: "apostles addressing church"
        translations:
          - lang: "tgl"
            word: "kami"
            hint: "exclusive (apostles, not congregation)"
      - context: "church unity passages"
        translations:
          - lang: "tgl"
            word: "tayo"
            hint: "inclusive (all believers together)"
```

---

For complete details, see the full analysis in the source files.
