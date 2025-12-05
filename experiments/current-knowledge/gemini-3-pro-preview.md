# TBTA Knowledge Snapshot - Gemini 3 Pro Preview

## What is TBTA?

TBTA (The Bible Translator's Assistant) is a computer-assisted translation system designed to facilitate the translation of the Bible into new languages. Unlike standard machine translation (which often relies on statistical or neural pairing of surface texts), TBTA uses a **semantic-based approach**. It relies on a rich, language-neutral semantic representation (often called the "semantic structure" or "deep structure") of the source text. This representation encodes the _meaning_ of the text (concepts, events, participants, and features) rather than its grammatical form. The system then uses a grammar of the target language (defined by a linguist or translator) to generate natural-sounding text in that target language from the semantic representation.

## Steps to Get to a Translated Verse

The general workflow in TBTA involves three main stages, often described as an **Analysis-Transfer-Synthesis** model, though TBTA focuses heavily on the generation side from a pre-analyzed source:

1.  **Semantic Analysis (Pre-processing):** The source text (Greek/Hebrew or English) is analyzed by experts to create the language-neutral Semantic Representations. This is often done once for the source text.
2.  **Grammar Definition:** The mother-tongue translator or linguist defines the grammar, lexicon, and transformation rules for the target language.
3.  **Generation/Synthesis:** The TBTA engine applies the target language grammar to the source Semantic Representations.
    - It maps universal concepts to target language words (Lexical Selection).
    - It organizes these words according to target syntax rules (Structural Adjustment).
    - It applies morphology (morphophonemics) to generate the final surface forms of words.

## Schema for Encoding Verses

The TBTA schema is hierarchical and event-focused. It typically includes:

- **Concepts:** Universally defined semantic units (e.g., `C:Run`, `C:John`, `C:God`). These are distinct from English words.
- **Event Structures:** Propositions containing a central Event (Verb/Predicate) and its Participants.
- **Semantic Roles (Thematic Roles):** Labels describing the relationship of participants to the event (e.g., Agent, Patient, Beneficiary, Source, Goal, Instrument).
- **Features:** Grammatical and semantic attributes attached to concepts, such as:
  - _Time/Tense_ (Past, Present, Future)
  - _Aspect_ (Perfective, Imperfective, Habitual)
  - _Mood_ (Indicative, Imperative, Subjunctive)
  - _Polarity_ (Positive, Negative)
  - _Person/Number/Gender_
  - _Discourse Features_ (Topic, Focus, Emphasis)

## 7 Most Important Steps to Encode a Verse

1.  **Identify the Main Event(s):** Determine the primary action or state of being in the clause (the predicate).
2.  **Identify Participants (Arguments):** Locate all entities involved in the event (Who did it? To whom? With what?).
3.  **Assign Semantic Roles:** Explicitly label the relationship of each participant to the event (e.g., tagging the "doer" as Agent).
4.  **Disambiguate Concepts:** Select the precise semantic concept for each word (e.g., distinguishing "bank" (river) from "bank" (finance)).
5.  **Determine Semantic Features:** Analyze the temporal and modal properties (Is it happening now? Is it a command? Is it negated?).
6.  **Establish Relationships:** Define how clauses relate to one another (Reason, Result, Temporal sequence) and handle reference tracking (pronouns/antecedents).
7.  **Structure the Hierarchy:** Organize the events and arguments into the correct dependency tree or nested structure required by the format.

## Encoded Verses

### 1. Genesis 1:1

**Text:** "In the beginning God created the heavens and the earth."
**Simplified:** `CREATE(Agent: God, Patient: Heavens_and_Earth, Time: Beginning)`

**Word Focus:** `CREATE`

**Phase 2 Dataframe Format:**
| ID | ParentID | Concept | Role | Category | Features |
|----|----------|---------|------|----------|----------|
| 1 | NULL | C:Create | Event | Verb | Tense:Past, Mood:Decl |
| 2 | 1 | C:God | Agent | Noun | Proper:True |
| 3 | 1 | C:Universe| Patient| Noun | Plural:False |

**Long JSON Format:**

```json
{
  "concept": "C:Create",
  "category": "Event",
  "features": {
    "time": "past",
    "mood": "declarative"
  },
  "arguments": [
    {
      "role": "Agent",
      "concept": "C:God",
      "features": { "proper": true }
    },
    {
      "role": "Patient",
      "concept": "C:Universe",
      "gloss": "heavens and earth",
      "features": { "number": "singular" }
    }
  ]
}
```

---

### 2. Ruth 2:4

**Text:** "And behold, Boaz came from Bethlehem..."
**Simplified:** `ARRIVE(Agent: Boaz, Source: Bethlehem, Attn: Behold)`

**Word Focus:** `BOAZ`

**Phase 2 Dataframe Format:**
| ID | ParentID | Concept | Role | Category | Features |
|----|----------|---------|------|----------|----------|
| 10 | 1 | C:Boaz | Agent | Noun | Gender:Male |

**Long JSON Format:**

```json
{
  "concept": "C:Boaz",
  "category": "Object",
  "role": "Agent",
  "features": {
    "gender": "male",
    "proper": true,
    "human": true
  },
  "parent_event": "C:Arrive"
}
```

---

### 3. Matthew 3:4

**Text:** "Now John wore a garment of camel's hair..."
**Simplified:** `WEAR(Agent: John, Patient: Garment, Material: Camel_Hair)`

**Word Focus:** `CAMEL`

**Phase 2 Dataframe Format:**
| ID | ParentID | Concept | Role | Category | Features |
|----|----------|---------|------|----------|----------|
| 5 | 4 | C:Camel | Possessor | Noun | Animate:True |

**Long JSON Format:**

```json
{
  "concept": "C:Camel",
  "category": "Object",
  "role": "Possessor",
  "relationships": {
    "modifies": "C:Hair"
  },
  "features": {
    "animate": true,
    "countable": true
  }
}
```

---

### 4. Romans 8:1

**Text:** "There is therefore now no condemnation for those who are in Christ Jesus."
**Simplified:** `EXIST(Patient: Condemnation, Polarity: Negative, Beneficiary: Those_In_Christ, Time: Now)`

**Word Focus:** `CONDEMNATION`

**Phase 2 Dataframe Format:**
| ID | ParentID | Concept | Role | Category | Features |
|----|----------|---------|------|----------|----------|
| 2 | 1 | C:Condemnation | Patient | Noun | Abstract:True |

**Long JSON Format:**

```json
{
  "concept": "C:Condemnation",
  "category": "Object",
  "role": "Patient",
  "features": {
    "abstract": true,
    "number": "singular"
  },
  "context": {
    "negated": true
  }
}
```

---

### 5. Ezekiel 12:3

**Text:** "Therefore, son of man, prepare for yourself an exile's baggage..."
**Simplified:** `PREPARE(Agent: Son_of_Man, Patient: Baggage, Purpose: Exile, Mode: Imperative)`

**Word Focus:** `BAGGAGE`

**Phase 2 Dataframe Format:**
| ID | ParentID | Concept | Role | Category | Features |
|----|----------|---------|------|----------|----------|
| 3 | 1 | C:Baggage | Patient | Noun | Concrete:True |

**Long JSON Format:**

```json
{
  "concept": "C:Baggage",
  "category": "Object",
  "role": "Patient",
  "features": {
    "concrete": true,
    "plural": false
  },
  "associations": {
    "type": "for_exile"
  }
}
```

---

### 6. Psalm 23:1

**Text:** "The Lord is my shepherd; I shall not want."
**Simplified:** `SHEPHERD(Agent: Lord, Patient: Me) AND WANT(Agent: Me, Polarity: Negative, Time: Future)`

**Word Focus:** `SHEPHERD`

**Phase 2 Dataframe Format:**
| ID | ParentID | Concept | Role | Category | Features |
|----|----------|---------|------|----------|----------|
| 1 | NULL | C:Shepherd | Event | Verb | Tense:Pres |

**Long JSON Format:**

```json
{
  "concept": "C:Shepherd",
  "category": "Event",
  "gloss": "to shepherd / to tend",
  "features": {
    "tense": "present",
    "aspect": "habitual"
  },
  "arguments": [
    { "role": "Agent", "concept": "C:Lord" },
    { "role": "Patient", "concept": "C:Me" }
  ]
}
```

---

### 7. John 3:16

**Text:** "For God so loved the world..."
**Simplified:** `LOVE(Agent: God, Patient: World, Degree: Greatly, Connection: Reason)`

**Word Focus:** `LOVE`

**Phase 2 Dataframe Format:**
| ID | ParentID | Concept | Role | Category | Features |
|----|----------|---------|------|----------|----------|
| 1 | NULL | C:Love | Event | Verb | Tense:Past |

**Long JSON Format:**

```json
{
  "concept": "C:Love",
  "category": "State/Event",
  "features": {
    "tense": "past",
    "mood": "indicative",
    "intensifier": "so/greatly"
  },
  "arguments": [
    { "role": "Agent", "concept": "C:God" },
    { "role": "Patient", "concept": "C:World" }
  ]
}
```
