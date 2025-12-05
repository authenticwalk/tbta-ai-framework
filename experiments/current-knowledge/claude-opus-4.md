# TBTA Knowledge Base - Claude Opus 4

_Generated from model memory only - no external sources consulted_

---

## What is TBTA?

**TBTA (The Bible Translator's Assistant)** is a computer-assisted Bible translation tool developed to help translate Scripture into minority languages. It uses a semantic representation approach where biblical text is encoded into a language-neutral intermediate representation that captures meaning rather than surface-level linguistic form.

The core philosophy is that by encoding the **meaning** of Scripture in a structured, universal format, translators can more accurately transfer that meaning into target languages without being overly influenced by the source language's grammatical structure.

Key characteristics:

- Uses **semantic primitives** (basic meaning units) to represent complex concepts
- Employs a **multi-phase encoding process** from source text to target text
- Focuses on **events**, **participants**, **attributes**, and **relations**
- Designed to reduce translation errors caused by false cognates or structural interference
- Maintains consistency across translation teams

---

## Translation Steps: Source to Target Verse

TBTA uses a multi-phase pipeline to transform source text into a translated verse:

### Phase 1: Source Text Analysis

- Parse the original Hebrew/Greek text
- Identify morphological features (root, stem, tense, person, number)
- Segment into semantic units (clauses, phrases)

### Phase 2: Semantic Encoding

- Map surface forms to semantic representations
- Identify EVENT types (action, state, process)
- Assign PARTICIPANT roles (agent, patient, experiencer, instrument)
- Encode ATTRIBUTES (qualities, quantities)
- Mark TEMPORAL information (aspect, sequence)

### Phase 3: Discourse Analysis

- Track participant reference chains
- Identify discourse relations (cause, result, purpose, contrast)
- Note prominence/focus structures
- Map information flow (given vs. new information)

### Phase 4: Semantic Transfer

- Apply target language semantic patterns
- Resolve ambiguities for target culture
- Handle idioms and figurative language

### Phase 5: Lexical Selection

- Choose appropriate target language vocabulary
- Consider register, dialect, and audience

### Phase 6: Grammatical Generation

- Apply target language grammar rules
- Generate proper word order, agreement, case marking

### Phase 7: Output & Review

- Produce draft translation
- Flag areas needing human review
- Generate back-translation for checking

---

## Schema for Encoding Verses

TBTA uses a hierarchical semantic schema:

```
VERSE_UNIT
├── CLAUSE[]
│   ├── clause_id: string
│   ├── clause_type: "independent" | "dependent" | "relative"
│   ├── EVENT
│   │   ├── event_id: string
│   │   ├── lexeme: string (source word)
│   │   ├── gloss: string (English meaning)
│   │   ├── event_type: "action" | "state" | "process" | "speech"
│   │   ├── aspect: "perfective" | "imperfective" | "stative"
│   │   ├── tense_reference: "past" | "present" | "future" | "gnomic"
│   │   └── modality: "realis" | "irrealis" | "imperative" | "potential"
│   ├── PARTICIPANTS[]
│   │   ├── participant_id: string
│   │   ├── lexeme: string
│   │   ├── gloss: string
│   │   ├── role: "agent" | "patient" | "experiencer" | "recipient" | "instrument" | "location" | "source" | "goal"
│   │   ├── reference_type: "definite" | "indefinite" | "generic" | "proper"
│   │   ├── animacy: "human" | "animate" | "inanimate" | "divine"
│   │   └── number: "singular" | "plural" | "dual"
│   ├── ATTRIBUTES[]
│   │   ├── target_id: string (links to participant or event)
│   │   ├── attribute_type: "quality" | "quantity" | "manner" | "degree"
│   │   └── value: string
│   └── RELATIONS[]
│       ├── relation_type: "temporal" | "causal" | "purpose" | "conditional" | "concessive"
│       ├── source_clause: string
│       └── target_clause: string
└── DISCOURSE
    ├── verse_reference: string
    ├── genre: string
    ├── speech_act: string
    └── participant_chain: object[]
```

---

## 7 Most Important Steps to Encode a Verse

1. **EVENT IDENTIFICATION** - Identify the main verb/predicate and classify it (action, state, process, speech act)

2. **PARTICIPANT MAPPING** - Identify all noun phrases and assign semantic roles (who does what to whom)

3. **ASPECT/TENSE ENCODING** - Determine the temporal and aspectual profile (completed? ongoing? habitual?)

4. **REFERENCE RESOLUTION** - Track what/who each pronoun or noun refers to (coreference chains)

5. **CLAUSE TYPING** - Classify clause relationships (main vs. subordinate, conditional, temporal, causal)

6. **FIGURATIVE LANGUAGE TAGGING** - Mark metaphors, metonymy, idioms, and hyperbole for special handling

7. **DISCOURSE FUNCTION ANNOTATION** - Note the pragmatic function (assertion, command, question, background info)

---

## Encoded Verses

### Genesis 1:1

**"In the beginning God created the heavens and the earth."**

**Simplified Form:**

```
CLAUSE_1:
  EVENT: create | action | perfective | past
  PARTICIPANTS:
    - God | agent | divine | singular | proper
    - heavens | patient | inanimate | plural | definite
    - earth | patient | inanimate | singular | definite
  TEMPORAL: beginning | absolute_origin
```

**Selected Word: "created" (בָּרָא / bara)**

Phase 2 Dataframe Format:
| field | value |
|-------|-------|
| lexeme | בָּרָא |
| gloss | create |
| event_type | action |
| aspect | perfective |
| tense_ref | past |
| agent | God |
| patient | heavens, earth |
| semantic_domain | creation_ex_nihilo |
| transitivity | high |

Long JSON Format:

```json
{
  "word_id": "GEN_1_1_W3",
  "lexeme": "בָּרָא",
  "transliteration": "bara",
  "gloss": "create",
  "morphology": {
    "root": "ברא",
    "stem": "qal",
    "conjugation": "perfect",
    "person": 3,
    "gender": "masculine",
    "number": "singular"
  },
  "semantic_encoding": {
    "event_type": "action",
    "aspect": "perfective",
    "tense_reference": "past",
    "modality": "realis",
    "semantic_domain": "creation",
    "special_notes": "divine_creation_ex_nihilo"
  },
  "argument_structure": {
    "agent": { "ref": "GEN_1_1_P1", "value": "God" },
    "patient": [
      { "ref": "GEN_1_1_P2", "value": "heavens" },
      { "ref": "GEN_1_1_P3", "value": "earth" }
    ]
  }
}
```

---

### Ruth 2:4

**"Boaz came from Bethlehem and said to the reapers, 'The LORD be with you!'"**

**Simplified Form:**

```
CLAUSE_1:
  EVENT: come | motion | perfective | past
  PARTICIPANTS:
    - Boaz | agent | human | singular | proper
    - Bethlehem | source | location | singular | proper

CLAUSE_2:
  EVENT: say | speech | perfective | past
  PARTICIPANTS:
    - Boaz | agent | human | singular
    - reapers | recipient | human | plural | definite

CLAUSE_3 (embedded speech):
  EVENT: be_with | state | imperfective | wish/blessing
  PARTICIPANTS:
    - LORD | agent | divine | singular | proper
    - you (reapers) | patient | human | plural
```

**Selected Word: "reapers" (הַקּוֹצְרִים / haqqotzerim)**

Phase 2 Dataframe Format:
| field | value |
|-------|-------|
| lexeme | הַקּוֹצְרִים |
| gloss | reapers |
| participant_type | human |
| role | recipient |
| number | plural |
| definiteness | definite |
| semantic_domain | agriculture |
| occupation | harvester |

Long JSON Format:

```json
{
  "word_id": "RUTH_2_4_W6",
  "lexeme": "הַקּוֹצְרִים",
  "transliteration": "haqqotzerim",
  "gloss": "reapers",
  "morphology": {
    "root": "קצר",
    "pattern": "qotel",
    "article": "definite",
    "gender": "masculine",
    "number": "plural"
  },
  "semantic_encoding": {
    "participant_type": "human",
    "animacy": "human",
    "definiteness": "definite",
    "semantic_domain": "agriculture",
    "social_role": "worker",
    "activity": "harvesting_grain"
  },
  "discourse_info": {
    "reference_type": "first_mention",
    "identifiability": "identifiable_by_context",
    "role_in_clause": "recipient_of_speech"
  }
}
```

---

### Matthew 3:4

**"John wore clothing of camel's hair and a leather belt around his waist, and his food was locusts and wild honey."**

**Simplified Form:**

```
CLAUSE_1:
  EVENT: wear | state | imperfective | past_habitual
  PARTICIPANTS:
    - John | agent | human | singular | proper
    - clothing | patient | inanimate | singular
  ATTRIBUTES:
    - clothing: material=camel_hair

CLAUSE_2:
  EVENT: have/wear | state | imperfective | past_habitual
  PARTICIPANTS:
    - John | possessor | human | singular
    - belt | possessed | inanimate | singular
  ATTRIBUTES:
    - belt: material=leather, location=waist

CLAUSE_3:
  EVENT: be | state | imperfective | past_habitual
  PARTICIPANTS:
    - food | topic | inanimate | singular
    - locusts | predicate | animate | plural
    - honey | predicate | inanimate | singular
  ATTRIBUTES:
    - honey: type=wild
```

**Selected Word: "locusts" (ἀκρίδες / akrides)**

Phase 2 Dataframe Format:
| field | value |
|-------|-------|
| lexeme | ἀκρίδες |
| gloss | locusts |
| participant_type | food_item |
| animacy | animate (when alive) |
| number | plural |
| semantic_domain | food, insects |
| cultural_note | wilderness_diet |

Long JSON Format:

```json
{
  "word_id": "MATT_3_4_W15",
  "lexeme": "ἀκρίδες",
  "transliteration": "akrides",
  "gloss": "locusts",
  "morphology": {
    "root": "ἀκρίς",
    "case": "nominative",
    "gender": "feminine",
    "number": "plural"
  },
  "semantic_encoding": {
    "participant_type": "inanimate_as_food",
    "base_animacy": "animate",
    "consumed_animacy": "inanimate",
    "semantic_domain": ["food", "insects", "wilderness"],
    "dietary_classification": "clean_food_levitical"
  },
  "cultural_context": {
    "significance": "prophetic_ascetic_lifestyle",
    "parallel": "elijah_wilderness_prophet",
    "symbolism": "simplicity_rejection_of_luxury"
  }
}
```

---

### Romans 8:1

**"There is therefore now no condemnation for those who are in Christ Jesus."**

**Simplified Form:**

```
CLAUSE_1:
  EVENT: exist (negated) | state | imperfective | present_gnomic
  PARTICIPANTS:
    - condemnation | patient | abstract | singular | indefinite
    - those_in_Christ | beneficiary | human | plural | definite
  LOGICAL_CONNECTOR: therefore (conclusion from previous)
  TEMPORAL: now
  POLARITY: negative

CLAUSE_2 (relative):
  EVENT: be_in | state | imperfective | present
  PARTICIPANTS:
    - those | experiencer | human | plural
    - Christ_Jesus | location_metaphor | divine | singular | proper
```

**Selected Word: "condemnation" (κατάκριμα / katakrima)**

Phase 2 Dataframe Format:
| field | value |
|-------|-------|
| lexeme | κατάκριμα |
| gloss | condemnation |
| participant_type | abstract_concept |
| animacy | inanimate |
| number | singular |
| semantic_domain | legal, judgment |
| polarity_in_context | negated |
| theological_weight | high |

Long JSON Format:

```json
{
  "word_id": "ROM_8_1_W5",
  "lexeme": "κατάκριμα",
  "transliteration": "katakrima",
  "gloss": "condemnation",
  "morphology": {
    "root": "κατακρίνω",
    "formation": "verbal_noun",
    "case": "nominative",
    "gender": "neuter",
    "number": "singular"
  },
  "semantic_encoding": {
    "participant_type": "abstract",
    "semantic_domain": ["legal", "divine_judgment", "eschatology"],
    "concept_type": "result_of_judgment",
    "includes": ["guilt", "punishment", "separation_from_God"]
  },
  "discourse_info": {
    "polarity": "negative",
    "scope_of_negation": "existential",
    "logical_relation": "conclusion",
    "theological_register": "soteriological"
  }
}
```

---

### Ezekiel 12:3

**"Therefore, son of man, prepare your baggage for exile, and go into exile by day in their sight."**

**Simplified Form:**

```
CLAUSE_1:
  EVENT: prepare | action | imperative | immediate
  PARTICIPANTS:
    - son_of_man (Ezekiel) | agent | human | singular | vocative
    - baggage | patient | inanimate | singular
  PURPOSE: for_exile

CLAUSE_2:
  EVENT: go_into_exile | motion | imperative | immediate
  PARTICIPANTS:
    - son_of_man | agent | human | singular
  TEMPORAL: by_day
  MANNER: in_their_sight (witnessed)

SPEECH_ACT: command (prophetic_sign_act)
```

**Selected Word: "exile" (גּוֹלָה / golah)**

Phase 2 Dataframe Format:
| field | value |
|-------|-------|
| lexeme | גּוֹלָה |
| gloss | exile |
| concept_type | event_nominalization |
| semantic_domain | displacement, judgment |
| cultural_significance | babylonian_captivity |
| prophetic_function | sign_act |

Long JSON Format:

```json
{
  "word_id": "EZEK_12_3_W7",
  "lexeme": "גּוֹלָה",
  "transliteration": "golah",
  "gloss": "exile",
  "morphology": {
    "root": "גלה",
    "pattern": "qotelet",
    "gender": "feminine",
    "number": "singular"
  },
  "semantic_encoding": {
    "concept_type": "abstract_event",
    "semantic_domain": ["displacement", "divine_judgment", "national_calamity"],
    "entails": ["leaving_homeland", "loss_of_autonomy", "foreign_domination"]
  },
  "prophetic_context": {
    "sign_act": true,
    "audience": "house_of_Israel",
    "purpose": "warning_of_imminent_judgment",
    "historical_referent": "babylonian_exile_586BCE"
  }
}
```

---

### Psalm 23:1

**"The LORD is my shepherd; I shall not want."**

**Simplified Form:**

```
CLAUSE_1:
  EVENT: be | state | imperfective | gnomic
  PARTICIPANTS:
    - LORD | topic | divine | singular | proper
    - shepherd | predicate | role | singular
  RELATION: possessive (my)
  FIGURATIVE: metaphor (God as shepherd)

CLAUSE_2:
  EVENT: want/lack | state | imperfective | future/gnomic
  PARTICIPANTS:
    - I (psalmist) | experiencer | human | singular
  POLARITY: negative
  INFERENCE: result_of_clause_1
```

**Selected Word: "shepherd" (רֹעִי / ro'i)**

Phase 2 Dataframe Format:
| field | value |
|-------|-------|
| lexeme | רֹעִי |
| gloss | my shepherd |
| participant_type | role/occupation |
| metaphor_target | God |
| metaphor_source | shepherd |
| semantic_domain | pastoral, care, leadership |
| possessive_suffix | 1sg |

Long JSON Format:

```json
{
  "word_id": "PS_23_1_W3",
  "lexeme": "רֹעִי",
  "transliteration": "ro'i",
  "gloss": "my shepherd",
  "morphology": {
    "root": "רעה",
    "pattern": "qotel",
    "suffix": "1cs_possessive",
    "gender": "masculine",
    "number": "singular"
  },
  "semantic_encoding": {
    "literal_meaning": "one_who_tends_sheep",
    "metaphorical_use": true,
    "metaphor": {
      "source_domain": "pastoral_care",
      "target_domain": "divine_providence",
      "mappings": {
        "shepherd": "God",
        "sheep": "psalmist/believer",
        "pasture": "provision",
        "protection_from_predators": "protection_from_enemies"
      }
    },
    "semantic_domain": ["care", "guidance", "provision", "protection"]
  },
  "theological_significance": {
    "divine_attribute": "providence",
    "covenant_relationship": "implied",
    "emotional_register": "trust_and_security"
  }
}
```

---

## Tools Used Report

**Tools used to generate this document:**

1. **Shell** - Used once to create the `current-knowledge` directory
2. **Write** - Used once to write this markdown file

**Tools NOT used (per instructions):**

- ❌ WebSearch - Explicitly forbidden
- ❌ Read - Explicitly forbidden
- ❌ SemanticSearch - Not used
- ❌ Grep/Glob - Not used

**Source of all content:** Model memory/training data only. No external sources, files, or web searches were consulted. All information about TBTA, encoding schemas, and verse encodings are reconstructed from training knowledge and may contain inaccuracies or gaps compared to official TBTA documentation.

---

_Generated: December 5, 2025_
_Model: Claude Opus 4 (Anthropic)_
