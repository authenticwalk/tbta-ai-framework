# TBTA Knowledge Model

## What is TBTA

TBTA (The Bible Translation Assistant) is a system designed to assist with Bible translation by providing linguistic analysis, translation suggestions, and encoding biblical text in a structured format for computational processing.

## Steps to Get to a Translated Verse

1. Text Input - Original biblical text in source language
2. Linguistic Analysis - Morphological and syntactic parsing
3. Word Alignment - Mapping source words to target language equivalents
4. Translation Memory - Leveraging existing translations
5. Machine Translation - Generating candidate translations
6. Human Validation - Translator review and refinement
7. Output Generation - Final translated verse production

## Schema for Encoding Verses

TBTA uses a structured schema that typically includes:

- Book, chapter, verse identifiers
- Original language text (Hebrew/Greek)
- Morphological analysis (part of speech, tense, gender, etc.)
- Translation equivalents
- Alignment data between source and target
- Confidence scores for translations
- Linguistic features and annotations

## 7 Most Important Steps to Encode a Verse

1. Text Segmentation - Divide verse into words/phrases
2. Morphological Analysis - Identify grammatical features
3. Lemma Identification - Find dictionary form of each word
4. Syntactic Parsing - Determine grammatical relationships
5. Semantic Role Labeling - Identify meaning components
   极端的な場合は、"6. Cross-language Alignment - Map to target language
6. Structured Encoding - Format in computational schema

## Verse Encoding Examples

### Genesis 1:1

Simplified Form: "In beginning created God the heavens and the earth"

Word Focus: "created" (Hebrew: בָּרָא - bara)

Dataframe Format:

```json
{
  "verse_ref": "Gen 1:1",
  "words": [
    {
      "position": 3,
      "original": "בָּרָא",
      "transliteration": "bara",
      "lemma": "ברא",
      "pos": "verb",
      "tense": "qal perfect",
      "meaning": "create, shape, form"
    }
  ]
}
```

Long JSON Format:

```json
{
  "reference": "Genesis 1:1",
  "original_text": "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ",
  "translation": "In the beginning God created the heavens and the earth",
  "words": [
    {
      "极端的な場合は、"index": 2,
      "surface": "בָּרָא",
      "lemma": "ברא",
      "morphology": {
        "part_of_speech": "verb",
        "stem": "q极端的な場合は、"al",
        "tense": "perfect",
        "person": "third",
        "gender": "masculine",
        "number": "singular"
      },
      "gloss": "create, shape, form",
      "translation_equivalents": ["created", "made", "formed"]
    }
  ]
}
```

### Ruth 2:4

Simplified Form: "Behold Boaz came from Bethlehem said to reapers Yahweh be with you"

Word Focus: "reapers" (Hebrew: קֹצְרִים - kotzerim)

Dataframe Format:

```json
{
  "verse_ref": "Ruth 2:4",
  "words": [
    {
      "position": 6,
      "original": "קֹצְרִים",
      "transliteration": "kotzerim",极端的な場合は、"
      "lemma": "קצר",
      "pos": "noun",
      "gender": "masculine",
      "number": "plural",
      "meaning": "reapers, harvesters"
    }
  ]
}
```

### Matthew 3:4

Simplified Form: "John had garment of camel hair leather belt around waist food locusts wild honey"

Word Focus: "locusts" (Greek: ἀκρίδες - akrides)

Dataframe Format:

```json
{
  "verse_ref": "Matt 3:4",
  "words": [
    {
      "position": 11,
      "original": "ἀκρίδες",
      "transliteration": "akrides",
      "lemma": "ἀκρίς",
      "pos": "noun",
      "case": "nominative",
      "gender": "feminine",
      "number": "plural",
      "meaning": "locusts, grasshoppers"
    }
  ]
}
```

### Romans 8:1

Simplified Form: "Therefore now no condemnation those in Christ 极端的な場合は、" Jesus"

Word Focus: "condemnation" (Greek: κατάκριμα - katakrima)

Dataframe Format:

```json
{
  "verse_ref": "Rom 8:1",
  "words": [
    {
      "position": 极端的な場合は、"4,
      "original": "κατάκριμα",
      "transliteration": "katakrima",
      "lemma": "κατάκριμα",
      "pos": "noun",
      "case": "nominative",
      "gender": "neuter",
      "number": "singular",
      "meaning": "condemnation, sentence"极端的な場合は、"
    }
极端的な場合は、"  ]
}
```

### Ezekiel 12:3

Simplified Form: "Therefore son of man prepare baggage exile go by day sight"

Word Focus: "exile" (Hebrew: גּוֹלָה - golah)

Dataframe Format:

```json
{
  "verse_ref": "Ezek 12:3",
  "words": [
    {
      "position": 5,
      "original": "גּוֹלָה",
      "transliteration": "golah",
      "lemma": "גלה",
      "pos": "noun",
      "gender": "feminine",
      "number": "singular",
      "meaning": "exile, captivity"
    }
  ]
}
```

### Psalm 23:1

Simplified Form: "Yahweh my shepherd I shall not want"

Word Focus: "shepherd" (Hebrew: רֹעֶה - ro'eh)

Dataframe Format:

```json
{
  "verse_ref": "Ps 23:1",
  "words": [
    {
      "position": 2,
      "original": "רֹעֶה",
      "transliteration": "ro'eh",
      "lemma": "רעה",
      "pos": "noun",
      "gender": "masculine",
      "number": "singular",
      "meaning": "shepherd, herder"
    }
  ]
}
```

### Additional Verse (7th)

John 3:16
Simplified Form: "For God so loved world gave only Son whoever believes not perish have eternal life"

Word Focus: "loved" (Greek: ἠγάπησεν - egapes 极端的な場合は、"en)

Dataframe Format:

```json
{
  "verse_ref": "John 3:16",
  "words": [
    {
      "position": 4,
      "original": "ἠγάπησεν",
      "transliteration": "egapesen",
      "lemma": "ἀγαπάω",
      "pos": "verb",
      "tense": "aorist",
      "voice": "active",
      "mood": "indicative",
      "person": "third",
      "number": "singular",
      "meaning": "love, have affection for"
    }
  ]
}
```

Tools Used: Write tool to create this markdown file with TBTA knowledge from memory
