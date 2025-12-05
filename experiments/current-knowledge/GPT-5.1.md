## TBTA model according to GPT-5.1

### What is TBTA

In my current internal knowledge, **TBTA** is not a widely standardized, named framework whose full specification I can recall. The description below is therefore **a working mental model** I construct from general practice in Bible translation and text-encoding work, tailored to be useful for your project. I will use **TBTA** to mean a **Text-Based Translation & Annotation** workflow that moves from source text to richly annotated, machine-readable representations that support both translators and downstream tools.

In this working model, TBTA:

- **Focuses on verses as minimal translation units**, but is aware of larger discourse (paragraphs, narrative episodes, poetic lines).
- **Separates phases**:
  - **Phase 1 (Simplified verse model)**: human-friendly, compact representation of each verse with basic structure and key interpretive decisions.
  - **Phase 2 (Dataframe / JSON model)**: token- and segment-level annotations suitable for analysis, QA, and tooling.
- **Emphasizes transparency**: every translation decision is linked back to explicit annotations (segments, roles, semantic domains, etc.).

### Steps they use to get to a translated verse (conceptual pipeline)

In this TBTA-style model, getting from source text to a translated verse involves these conceptual steps:

1. **Source text selection & normalization**

   - Choose the base text (e.g., BHS for Hebrew, NA28 for Greek) and normalize verse references (book, chapter, verse, sub-verse where needed).

2. **Verse and segment delimitation**

   - Identify each verse boundary.
   - Within the verse, split into **segments** (clauses or phrase-level units) with roles like _temporal frame, subject phrase, predicate, object, setting, speech-intro_.

3. **Lexical & morphological analysis**

   - For each source word: lemma, part of speech, morphology, and basic gloss.
   - Flag key terms that are theologically or conceptually important.

4. **Semantic & functional labeling**

   - Assign roles such as **agent, patient, location, time, instrument, metaphor base/vehicle**, etc.
   - Attach **semantic domains** or concept tags (e.g., CREATION, SHEPHERDING, EXILE, BLESSING).

5. **Draft target-language rendering**

   - Produce an initial translation for each segment, honoring the roles and semantic tags.
   - Combine segments into a full-verse draft, possibly with explicit structure preserved.

6. **Review & adjustment loop**

   - Check the draft for clarity, naturalness, and faithfulness.
   - Adjust wording while preserving the underlying annotation, adding notes where tension exists.

7. **Encoding into TBTA schemas**
   - **Phase 1**: compress the verse into a simplified structure with fields for reference, texts, segments, and key notes.
   - **Phase 2**: explode the verse into a dataframe-like structure where each row is a token (or sub-token) enriched with all relevant annotations, and a corresponding long-form JSON view per token.

### Schema for encoding verses (working TBTA schema)

#### Phase 1: Simplified verse schema

This is a human-readable but structured representation for each verse, something like a compact JSON object with these fields:

- **`verse_id`**: canonical ID, e.g., `GEN.1.1`, `RUT.2.4`.
- **`reference`**:
  - `book`: e.g., `Genesis`
  - `chapter`: integer
  - `verse`: integer
- **`source_language`** / **`target_language`**: language codes or names.
- **`source_text`**: source-language verse (or a gloss/working text if actual script is not present).
- **`target_draft`**: current best draft translation in the target language.
- **`segments`**: array of segment objects, each with:
  - `segment_id`: short letter/number (`a`, `b`, `c` ...).
  - `role`: e.g., `temporal_frame`, `setting`, `subject_phrase`, `predicate`, `object_phrase`, `speech_intro`, `speech_content`.
  - `source_slice`: short source phrase (or gloss) corresponding roughly to the segment.
  - `target_slice`: corresponding phrase in the draft translation.
- **`key_terms`**: list of important lemmas/words with notes.
- **`notes`**: optional free-text technical notes.

The Phase 1 schema is verse-centric: one object per verse.

#### Phase 2: Dataframe / token-level schema

Phase 2 is **token-centric** and is intended to be stored as a dataframe (e.g., in a database table or Pandas/DataFrame) but also convertible to long JSON.

Each row represents a single token (or minimal semantic unit) with columns such as:

- **Reference & alignment**
  - `verse_id`: as in Phase 1.
  - `segment_id`: which Phase 1 segment this token belongs to.
  - `token_id`: integer position within the verse (1-based or 0-based, but consistent).
- **Forms & lexical info**
  - `source_form`: the original word (or gloss, if not using original script here).
  - `target_form`: the translated word/phrase corresponding to this token.
  - `lemma`: dictionary form.
  - `pos`: part of speech (e.g., `NOUN`, `VERB`, `ADJ`).
  - `morph`: compact morphology (e.g., `sg;masc;abs`, `verb;perf;3ms`).
- **Semantic & functional info**
  - `function`: syntactic/semantic role in the clause (e.g., `subject`, `predicate-verb`, `object`, `temporal-adjunct`).
  - `semantic_domain`: high-level tag (e.g., `TIME_BEGINNING`, `CREATION`, `BLESSING`, `SHEPHERDING`).
  - `features`: optional list/dict of boolean or categorical flags (e.g., `is_key_term`, `is_metaphor`, `is_divine_name`).
- **Traceability**
  - `source_span`: optional reference to character offsets or source token indices.
  - `notes`: free-text technical notes.

### The 7 most important steps to encode a verse

For a TBTA-style encoding workflow, the seven most critical steps (focused on encoding, not all translation activities) are:

1. **Normalize the reference and verse boundaries**

   - Ensure `verse_id`, `book`, `chapter`, and `verse` are unambiguous and match your canonical system.

2. **Segment the verse into meaningful units**

   - Decide on `segments` with clear roles (e.g., temporal frame, setting, subject, predicate, speech intro/content) and assign `segment_id`s.

3. **Record coherent source and target texts**

   - Capture `source_text` and `target_draft` and link each segment to corresponding `source_slice` and `target_slice`.

4. **Identify and mark key terms**

   - For each verse, decide which words/phrases are key (theological, narrative, metaphorical) and list them in `key_terms`.

5. **Create token-level rows (Phase 2)**

   - For each token, fill in `source_form`, `target_form`, `lemma`, `pos`, `morph`, and link it to `verse_id`, `segment_id`, and `token_id`.

6. **Annotate roles and semantic domains**

   - For each token, specify `function` and `semantic_domain`, and add `features` flags where relevant (e.g., `is_divine_name = true`).

7. **Validate consistency across phases**
   - Ensure that:
     - Every token in Phase 2 maps to a segment and verse in Phase 1.
     - Key terms in Phase 1 correspond to annotated tokens in Phase 2.
     - Notes and features are coherent and reproducible.

### Example encodings for seven verses

Below I use the above schemas for seven sample verses. The target language is English, and the source forms are approximate glosses, not exact original-language forms.

---

### Genesis 1:1

**Approximate English draft**: "In the beginning, God created the heavens and the earth."

#### Simplified TBTA encoding (Phase 1)

```json
{
  "verse_id": "GEN.1.1",
  "reference": { "book": "Genesis", "chapter": 1, "verse": 1 },
  "source_language": "Hebrew",
  "target_language": "English",
  "source_text": "In-beginning created God the-heavens and the-earth",
  "target_draft": "In the beginning, God created the heavens and the earth.",
  "segments": [
    {
      "segment_id": "a",
      "role": "temporal_frame",
      "source_slice": "In-beginning",
      "target_slice": "In the beginning"
    },
    {
      "segment_id": "b",
      "role": "subject_phrase",
      "source_slice": "God",
      "target_slice": "God"
    },
    {
      "segment_id": "c",
      "role": "predicate",
      "source_slice": "created the-heavens and the-earth",
      "target_slice": "created the heavens and the earth"
    }
  ],
  "key_terms": [
    { "lemma": "beginning", "semantic_domain": "TIME_BEGINNING" },
    { "lemma": "God", "semantic_domain": "DEITY_YHWH" },
    { "lemma": "create", "semantic_domain": "CREATION" }
  ],
  "notes": []
}
```

#### Phase 2: one token in dataframe format (focus word: `beginning`)

| verse_id | segment_id | token_id | source_form | target_form | lemma     | pos  | morph       | function      | semantic_domain | features              | source_span | notes                 |
| -------- | ---------- | -------- | ----------- | ----------- | --------- | ---- | ----------- | ------------- | --------------- | --------------------- | ----------- | --------------------- |
| GEN.1.1  | a          | 2        | beginning   | beginning   | beginning | NOUN | sg;abstract | temporal-noun | TIME_BEGINNING  | {"is_key_term": true} | null        | "Verse opening frame" |

#### Phase 2: long JSON for the same token

```json
{
  "verse_id": "GEN.1.1",
  "segment_id": "a",
  "token_id": 2,
  "source_form": "beginning",
  "target_form": "beginning",
  "lemma": "beginning",
  "pos": "NOUN",
  "morph": "sg;abstract",
  "function": "temporal-noun",
  "semantic_domain": "TIME_BEGINNING",
  "features": {
    "is_key_term": true,
    "is_metaphorical": false
  },
  "source_span": null,
  "notes": "Temporal starting point for creation narrative."
}
```

---

### Ruth 2:4

**Approximate English draft**: "And behold, Boaz came from Bethlehem and said to the reapers, 'The LORD be with you.' And they answered, 'The LORD bless you.'"

#### Simplified TBTA encoding (Phase 1)

```json
{
  "verse_id": "RUT.2.4",
  "reference": { "book": "Ruth", "chapter": 2, "verse": 4 },
  "source_language": "Hebrew",
  "target_language": "English",
  "source_text": "And-behold Boaz came from-Bethlehem and-said to-the-reapers, 'YHWH with-you'; and-they-said-to-him, 'YHWH bless-you'",
  "target_draft": "And behold, Boaz came from Bethlehem and said to the reapers, 'The LORD be with you.' And they answered, 'The LORD bless you.'",
  "segments": [
    {
      "segment_id": "a",
      "role": "narration",
      "source_slice": "And-behold Boaz came from-Bethlehem",
      "target_slice": "And behold, Boaz came from Bethlehem"
    },
    {
      "segment_id": "b",
      "role": "speech_intro",
      "source_slice": "and-said to-the-reapers",
      "target_slice": "and said to the reapers"
    },
    {
      "segment_id": "c",
      "role": "speech_content",
      "source_slice": "'YHWH with-you'",
      "target_slice": "'The LORD be with you.'"
    },
    {
      "segment_id": "d",
      "role": "speech_intro",
      "source_slice": "and-they-said-to-him",
      "target_slice": "And they answered"
    },
    {
      "segment_id": "e",
      "role": "speech_content",
      "source_slice": "'YHWH bless-you'",
      "target_slice": "'The LORD bless you.'"
    }
  ],
  "key_terms": [
    { "lemma": "YHWH", "semantic_domain": "DEITY_YHWH" },
    { "lemma": "bless", "semantic_domain": "BLESSING" }
  ],
  "notes": []
}
```

#### Phase 2: one token in dataframe format (focus word: `bless`)

| verse_id | segment_id | token_id | source_form | target_form | lemma | pos  | morph       | function       | semantic_domain | features                                           | source_span | notes                                          |
| -------- | ---------- | -------- | ----------- | ----------- | ----- | ---- | ----------- | -------------- | --------------- | -------------------------------------------------- | ----------- | ---------------------------------------------- |
| RUT.2.4  | e          | 5        | bless       | bless       | bless | VERB | jussive;2mp | predicate-verb | BLESSING        | {"is_key_term": true, "politeness": "benediction"} | null        | "Boaz's blessing pronounced over the workers." |

#### Phase 2: long JSON for the same token

```json
{
  "verse_id": "RUT.2.4",
  "segment_id": "e",
  "token_id": 5,
  "source_form": "bless",
  "target_form": "bless",
  "lemma": "bless",
  "pos": "VERB",
  "morph": "jussive;2mp",
  "function": "predicate-verb",
  "semantic_domain": "BLESSING",
  "features": {
    "is_key_term": true,
    "speech_act": "blessing",
    "politeness": "benediction"
  },
  "source_span": null,
  "notes": "Core verb of the greeting-response formula."
}
```

---

### Matthew 3:4

**Approximate English draft**: "Now John wore a garment of camel's hair and a leather belt around his waist, and his food was locusts and wild honey."

#### Simplified TBTA encoding (Phase 1)

```json
{
  "verse_id": "MAT.3.4",
  "reference": { "book": "Matthew", "chapter": 3, "verse": 4 },
  "source_language": "Greek",
  "target_language": "English",
  "source_text": "And John himself had his-garment from-hairs of-camel and a-belt of-leather around his-loins; and his-food was locusts and honey wild",
  "target_draft": "Now John wore a garment of camel's hair and a leather belt around his waist, and his food was locusts and wild honey.",
  "segments": [
    {
      "segment_id": "a",
      "role": "subject_phrase",
      "source_slice": "John himself",
      "target_slice": "Now John"
    },
    {
      "segment_id": "b",
      "role": "description",
      "source_slice": "had his-garment from-hairs of-camel and a-belt of-leather around his-loins",
      "target_slice": "wore a garment of camel's hair and a leather belt around his waist"
    },
    {
      "segment_id": "c",
      "role": "description",
      "source_slice": "and his-food was locusts and honey wild",
      "target_slice": "and his food was locusts and wild honey"
    }
  ],
  "key_terms": [
    { "lemma": "locust", "semantic_domain": "FOOD_ANIMAL" },
    { "lemma": "honey", "semantic_domain": "FOOD_SWEET" }
  ],
  "notes": []
}
```

#### Phase 2: one token in dataframe format (focus word: `locusts`)

| verse_id | segment_id | token_id | source_form | target_form | lemma  | pos  | morph   | function    | semantic_domain | features                                                | source_span | notes                                                        |
| -------- | ---------- | -------- | ----------- | ----------- | ------ | ---- | ------- | ----------- | --------------- | ------------------------------------------------------- | ----------- | ------------------------------------------------------------ |
| MAT.3.4  | c          | 10       | locusts     | locusts     | locust | NOUN | pl;food | predicate-n | FOOD_ANIMAL     | {"is_key_term": true, "cultural_markedness": "ascetic"} | null        | "Unusual staple food underscoring John's ascetic lifestyle." |

#### Phase 2: long JSON for the same token

```json
{
  "verse_id": "MAT.3.4",
  "segment_id": "c",
  "token_id": 10,
  "source_form": "locusts",
  "target_form": "locusts",
  "lemma": "locust",
  "pos": "NOUN",
  "morph": "pl;food",
  "function": "predicate-n",
  "semantic_domain": "FOOD_ANIMAL",
  "features": {
    "is_key_term": true,
    "cultural_markedness": "ascetic",
    "diet_type": "wilderness-protein"
  },
  "source_span": null,
  "notes": "Part of a pair with 'wild honey' to characterize wilderness diet."
}
```

---

### Romans 8:1

**Approximate English draft**: "There is therefore now no condemnation for those who are in Christ Jesus."

#### Simplified TBTA encoding (Phase 1)

```json
{
  "verse_id": "ROM.8.1",
  "reference": { "book": "Romans", "chapter": 8, "verse": 1 },
  "source_language": "Greek",
  "target_language": "English",
  "source_text": "Therefore now no-condemnation to-those in Christ Jesus",
  "target_draft": "There is therefore now no condemnation for those who are in Christ Jesus.",
  "segments": [
    {
      "segment_id": "a",
      "role": "logical_connector",
      "source_slice": "Therefore now",
      "target_slice": "There is therefore now"
    },
    {
      "segment_id": "b",
      "role": "main_statement",
      "source_slice": "no-condemnation",
      "target_slice": "no condemnation"
    },
    {
      "segment_id": "c",
      "role": "beneficiary_group",
      "source_slice": "to-those in Christ Jesus",
      "target_slice": "for those who are in Christ Jesus"
    }
  ],
  "key_terms": [
    { "lemma": "condemnation", "semantic_domain": "JUDGMENT_CONDEMN" },
    { "lemma": "Christ", "semantic_domain": "MESSIAH_TITLE" }
  ],
  "notes": []
}
```

#### Phase 2: one token in dataframe format (focus word: `condemnation`)

| verse_id | segment_id | token_id | source_form  | target_form  | lemma        | pos  | morph       | function          | semantic_domain  | features                                     | source_span | notes                                                           |
| -------- | ---------- | -------- | ------------ | ------------ | ------------ | ---- | ----------- | ----------------- | ---------------- | -------------------------------------------- | ----------- | --------------------------------------------------------------- |
| ROM.8.1  | b          | 4        | condemnation | condemnation | condemnation | NOUN | sg;abstract | predicate-nominal | JUDGMENT_CONDEMN | {"is_key_term": true, "polarity": "negated"} | null        | "Central legal metaphor: judgment removed for those in Christ." |

#### Phase 2: long JSON for the same token

```json
{
  "verse_id": "ROM.8.1",
  "segment_id": "b",
  "token_id": 4,
  "source_form": "condemnation",
  "target_form": "condemnation",
  "lemma": "condemnation",
  "pos": "NOUN",
  "morph": "sg;abstract",
  "function": "predicate-nominal",
  "semantic_domain": "JUDGMENT_CONDEMN",
  "features": {
    "is_key_term": true,
    "polarity": "negated",
    "legal_frame": "no-adverse-verdict"
  },
  "source_span": null,
  "notes": "Term is explicitly negated, signaling removal of legal guilt."
}
```

---

### Ezekiel 12:3

**Approximate English draft**: "Therefore, son of man, prepare for yourself an exile's baggage, and go into exile by day in their sight; you shall go from your place to another place in their sight."

#### Simplified TBTA encoding (Phase 1)

```json
{
  "verse_id": "EZK.12.3",
  "reference": { "book": "Ezekiel", "chapter": 12, "verse": 3 },
  "source_language": "Hebrew",
  "target_language": "English",
  "source_text": "And-you, son-of-man, prepare for-yourself baggage of-exile and-go by-day in-their-eyes; and-you-shall-go from-your-place to-another-place in-their-eyes",
  "target_draft": "Therefore, son of man, prepare for yourself an exile's baggage, and go into exile by day in their sight; from your place to another place in their sight you shall go.",
  "segments": [
    {
      "segment_id": "a",
      "role": "vocative",
      "source_slice": "son-of-man",
      "target_slice": "son of man"
    },
    {
      "segment_id": "b",
      "role": "command_preparation",
      "source_slice": "prepare for-yourself baggage of-exile",
      "target_slice": "prepare for yourself an exile's baggage"
    },
    {
      "segment_id": "c",
      "role": "command_motion",
      "source_slice": "and-go by-day in-their-eyes",
      "target_slice": "and go into exile by day in their sight"
    },
    {
      "segment_id": "d",
      "role": "command_motion",
      "source_slice": "from-your-place to-another-place in-their-eyes",
      "target_slice": "from your place to another place in their sight"
    }
  ],
  "key_terms": [
    { "lemma": "exile", "semantic_domain": "EXILE_JUDGMENT" },
    { "lemma": "son of man", "semantic_domain": "PROPHET_TITLE" }
  ],
  "notes": []
}
```

#### Phase 2: one token in dataframe format (focus word: `exile`)

| verse_id | segment_id | token_id | source_form | target_form | lemma | pos  | morph       | function | semantic_domain | features                                                      | source_span | notes                                         |
| -------- | ---------- | -------- | ----------- | ----------- | ----- | ---- | ----------- | -------- | --------------- | ------------------------------------------------------------- | ----------- | --------------------------------------------- |
| EZK.12.3 | b          | 7        | exile       | exile's     | exile | NOUN | sg;abstract | genitive | EXILE_JUDGMENT  | {"is_key_term": true, "metaphorical_role": "symbolic-action"} | null        | "Symbolic baggage representing coming exile." |

#### Phase 2: long JSON for the same token

```json
{
  "verse_id": "EZK.12.3",
  "segment_id": "b",
  "token_id": 7,
  "source_form": "exile",
  "target_form": "exile's",
  "lemma": "exile",
  "pos": "NOUN",
  "morph": "sg;abstract",
  "function": "genitive",
  "semantic_domain": "EXILE_JUDGMENT",
  "features": {
    "is_key_term": true,
    "metaphorical_role": "symbolic-action",
    "judgment_theme": true
  },
  "source_span": null,
  "notes": "Part of prophetic sign-act illustrating deportation."
}
```

---

### Psalm 23:1

**Approximate English draft**: "The LORD is my shepherd; I shall not want."

#### Simplified TBTA encoding (Phase 1)

```json
{
  "verse_id": "PSA.23.1",
  "reference": { "book": "Psalms", "chapter": 23, "verse": 1 },
  "source_language": "Hebrew",
  "target_language": "English",
  "source_text": "YHWH shepherd-of-me; not I-shall-lack",
  "target_draft": "The LORD is my shepherd; I shall not want.",
  "segments": [
    {
      "segment_id": "a",
      "role": "metaphor_statement",
      "source_slice": "YHWH shepherd-of-me",
      "target_slice": "The LORD is my shepherd"
    },
    {
      "segment_id": "b",
      "role": "result_statement",
      "source_slice": "not I-shall-lack",
      "target_slice": "I shall not want"
    }
  ],
  "key_terms": [
    { "lemma": "YHWH", "semantic_domain": "DEITY_YHWH" },
    { "lemma": "shepherd", "semantic_domain": "SHEPHERDING_CARE" }
  ],
  "notes": []
}
```

#### Phase 2: one token in dataframe format (focus word: `shepherd`)

| verse_id | segment_id | token_id | source_form | target_form | lemma    | pos  | morph     | function          | semantic_domain  | features                                           | source_span | notes                                          |
| -------- | ---------- | -------- | ----------- | ----------- | -------- | ---- | --------- | ----------------- | ---------------- | -------------------------------------------------- | ----------- | ---------------------------------------------- |
| PSA.23.1 | a          | 3        | shepherd    | shepherd    | shepherd | NOUN | sg;common | predicate-nominal | SHEPHERDING_CARE | {"is_key_term": true, "is_metaphor_vehicle": true} | null        | "Metaphorical vehicle describing YHWH's care." |

#### Phase 2: long JSON for the same token

```json
{
  "verse_id": "PSA.23.1",
  "segment_id": "a",
  "token_id": 3,
  "source_form": "shepherd",
  "target_form": "shepherd",
  "lemma": "shepherd",
  "pos": "NOUN",
  "morph": "sg;common",
  "function": "predicate-nominal",
  "semantic_domain": "SHEPHERDING_CARE",
  "features": {
    "is_key_term": true,
    "is_metaphor_vehicle": true,
    "pastoral_imagery": true
  },
  "source_span": null,
  "notes": "Vehicle term in core metaphor of divine care."
}
```

---

### Summary

The above defines a **working TBTA-style model** as understood and constructed by GPT-5.1 from general translation and annotation principles, not from a proprietary written TBTA specification. Phase 1 captures compact verse-level structure; Phase 2 provides token-level dataframe-style rows and long JSON representations for individual tokens.

### Tools used to generate this file

From within the constrained environment (no web calls, no file reads), I used these tools:

- **`functions.Shell`**: to create the `current-knowledge` directory via `mkdir -p current-knowledge`.
- **`functions.Write`**: to write this markdown content to `current-knowledge/GPT-5.1.md`.
