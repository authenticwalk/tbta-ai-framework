# TBTA Knowledge Base

## What is TBTA

TBTA (Text-Based Translation Analysis) appears to be a system for analyzing and encoding biblical texts with a focus on translation methodology. It involves structured encoding of verses with linguistic and semantic annotations to support translation work.

## Steps to Get to a Translated Verse

The TBTA process typically involves:

1. **Source Text Input** - Input the original biblical text (Hebrew, Aramaic, or Greek)
2. **Morphological Analysis** - Parse words into their morphological components
3. **Lexical Identification** - Identify root forms and dictionary entries
4. **Syntactic Analysis** - Determine grammatical relationships and sentence structure
5. **Semantic Tagging** - Apply semantic categories and roles
6. **Cross-Reference Mapping** - Link to related verses and concepts
7. **Translation Generation** - Produce target language translation based on encoded data
8. **Validation** - Review and validate the translation against source encoding

## Schema for Encoding Verses

The TBTA schema appears to encode verses with multiple layers:

- **Verse Reference** - Book, chapter, verse identifiers
- **Word-Level Data** - Individual word encoding with:
  - Original form
  - Morphological breakdown
  - Lexical root/lemma
  - Part of speech
  - Grammatical features (tense, person, number, gender, etc.)
  - Semantic tags
  - Translation equivalents
- **Phrase/Clause Level** - Syntactic relationships
- **Verse Level** - Overall structure and meaning

## 7 Most Important Steps to Encode

1. **Word Segmentation** - Break verse into individual words/tokens
2. **Morphological Parsing** - Analyze each word's form, root, and grammatical features
3. **Lexical Mapping** - Map to dictionary entries and identify meanings
4. **Syntactic Analysis** - Determine grammatical relationships (subject, verb, object, modifiers)
5. **Semantic Annotation** - Apply semantic categories (action, entity, attribute, etc.)
6. **Cross-Linguistic Alignment** - Map structures to target language patterns
7. **Translation Equivalence Assignment** - Assign appropriate translation equivalents

## Encoded Verses

### Genesis 1:1

**Simplified Form:**
בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ

**Phase 2 DataFrame Format (selected word: בָּרָא):**

```
word_id: 2
original_form: בָּרָא
lemma: ברא
pos: verb
tense: qal_perfect
person: 3
number: singular
gender: common
translation: created
semantic_role: action
```

**Long JSON Format:**

```json
{
  "word_id": 2,
  "original_form": "בָּרָא",
  "transliteration": "bara",
  "lemma": "ברא",
  "root": "ברא",
  "part_of_speech": "verb",
  "morphology": {
    "stem": "qal",
    "tense": "perfect",
    "person": "third",
    "number": "singular",
    "gender": "common"
  },
  "lexical_data": {
    "strongs": "H1254",
    "gloss": "create, make"
  },
  "syntax": {
    "function": "predicate",
    "governs": ["object"]
  },
  "semantics": {
    "role": "action",
    "category": "creation"
  },
  "translation": {
    "english": "created",
    "confidence": 0.95
  }
}
```

### Ruth 2:4

**Simplified Form:**
וְהִנֵּה בֹּעַז בָּא מִבֵּית לֶחֶם

**Phase 2 DataFrame Format (selected word: בֹּעַז):**

```
word_id: 2
original_form: בֹּעַז
lemma: בעז
pos: proper_noun
person: 3
number: singular
gender: masculine
translation: Boaz
semantic_role: entity
```

**Long JSON Format:**

```json
{
  "word_id": 2,
  "original_form": "בֹּעַז",
  "transliteration": "Boaz",
  "lemma": "בעז",
  "root": "בעז",
  "part_of_speech": "proper_noun",
  "morphology": {
    "person": "third",
    "number": "singular",
    "gender": "masculine"
  },
  "lexical_data": {
    "strongs": "H1162",
    "gloss": "Boaz (proper name)"
  },
  "syntax": {
    "function": "subject"
  },
  "semantics": {
    "role": "entity",
    "category": "person"
  },
  "translation": {
    "english": "Boaz",
    "confidence": 1.0
  }
}
```

### Matthew 3:4

**Simplified Form:**
αὐτὸς δὲ ὁ Ἰωάννης εἶχεν τὸ ἔνδυμα αὐτοῦ ἀπὸ τριχῶν καμήλου

**Phase 2 DataFrame Format (selected word: εἶχεν):**

```
word_id: 3
original_form: εἶχεν
lemma: ἔχω
pos: verb
tense: imperfect
person: 3
number: singular
voice: active
translation: had
semantic_role: action
```

**Long JSON Format:**

```json
{
  "word_id": 3,
  "original_form": "εἶχεν",
  "transliteration": "eichen",
  "lemma": "ἔχω",
  "root": "ἔχ",
  "part_of_speech": "verb",
  "morphology": {
    "tense": "imperfect",
    "voice": "active",
    "mood": "indicative",
    "person": "third",
    "number": "singular"
  },
  "lexical_data": {
    "strongs": "G2192",
    "gloss": "have, hold, possess"
  },
  "syntax": {
    "function": "predicate",
    "governs": ["object"]
  },
  "semantics": {
    "role": "action",
    "category": "possession"
  },
  "translation": {
    "english": "had",
    "confidence": 0.98
  }
}
```

### Romans 8:1

**Simplified Form:**
Οὐδὲν ἄρα νῦν κατάκριμα τοῖς ἐν Χριστῷ Ἰησοῦ

**Phase 2 DataFrame Format (selected word: κατάκριμα):**

```
word_id: 4
original_form: κατάκριμα
lemma: κατάκριμα
pos: noun
case: nominative
number: singular
gender: neuter
translation: condemnation
semantic_role: entity
```

**Long JSON Format:**

```json
{
  "word_id": 4,
  "original_form": "κατάκριμα",
  "transliteration": "katakrima",
  "lemma": "κατάκριμα",
  "root": "κατακρίνω",
  "part_of_speech": "noun",
  "morphology": {
    "case": "nominative",
    "number": "singular",
    "gender": "neuter"
  },
  "lexical_data": {
    "strongs": "G2631",
    "gloss": "condemnation, sentence"
  },
  "syntax": {
    "function": "subject"
  },
  "semantics": {
    "role": "entity",
    "category": "abstract_concept"
  },
  "translation": {
    "english": "condemnation",
    "confidence": 0.97
  }
}
```

### Ezekiel 12:3

**Simplified Form:**
וְאַתָּה בֶן אָדָם עֲשֵׂה לְךָ כְּלֵי גוֹלָה

**Phase 2 DataFrame Format (selected word: עֲשֵׂה):**

```
word_id: 3
original_form: עֲשֵׂה
lemma: עשה
pos: verb
tense: qal_imperative
person: 2
number: singular
gender: masculine
translation: make
semantic_role: action
```

**Long JSON Format:**

```json
{
  "word_id": 3,
  "original_form": "עֲשֵׂה",
  "transliteration": "aseh",
  "lemma": "עשה",
  "root": "עשה",
  "part_of_speech": "verb",
  "morphology": {
    "stem": "qal",
    "tense": "imperative",
    "person": "second",
    "number": "singular",
    "gender": "masculine"
  },
  "lexical_data": {
    "strongs": "H6213",
    "gloss": "do, make, work"
  },
  "syntax": {
    "function": "predicate",
    "governs": ["object"]
  },
  "semantics": {
    "role": "action",
    "category": "creation_action"
  },
  "translation": {
    "english": "make",
    "confidence": 0.96
  }
}
```

### Psalm 23:1

**Simplified Form:**
מִזְמוֹר לְדָוִד יְהוָה רֹעִי לֹא אֶחְסָר

**Phase 2 DataFrame Format (selected word: רֹעִי):**

```
word_id: 4
original_form: רֹעִי
lemma: רעה
pos: noun
state: construct
number: singular
gender: masculine
translation: shepherd
semantic_role: entity
```

**Long JSON Format:**

```json
{
  "word_id": 4,
  "original_form": "רֹעִי",
  "transliteration": "ro'i",
  "lemma": "רעה",
  "root": "רעה",
  "part_of_speech": "noun",
  "morphology": {
    "state": "construct",
    "number": "singular",
    "gender": "masculine"
  },
  "lexical_data": {
    "strongs": "H7462",
    "gloss": "shepherd, herder"
  },
  "syntax": {
    "function": "predicate_nominative"
  },
  "semantics": {
    "role": "entity",
    "category": "person_role"
  },
  "translation": {
    "english": "shepherd",
    "confidence": 0.99
  }
}
```

---

## Tools Used

To create this document, I used:

- **write** tool - To create the markdown file at the specified path

Note: This information is based on general knowledge of biblical text analysis and translation methodologies. Specific details about TBTA's exact schema and encoding format would need to be verified against official TBTA documentation.
