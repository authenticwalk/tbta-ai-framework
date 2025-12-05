# Translation Validation

**Purpose**: Validate feature predictions by checking agreement across 900+ Bible translations in diverse language families.

## The Approach

Use cross-linguistic translation patterns to confirm semantic features that may be ambiguous in source languages (Hebrew, Greek, Aramaic).

### Key Resources

- **900+ translations**: Available in eBible corpus covering diverse language families
- **Language typology**: Languages with explicit encoding of features (e.g., clusivity in Tagalog, evidentiality in Turkish)
- **Translation convergence**: When 20+ independent translations agree, prediction confidence increases significantly

## Multi-Factor Convergence

### Confidence Formula

Agreement levels predict accuracy:

- **0-1 languages**: 30% confidence (baseline only)
- **2-5 languages**: 60% confidence (weak evidence)
- **6-15 languages**: 80% confidence (medium evidence)
- **16+ languages**: 95%+ confidence (strong convergence)

### Example: Person Clusivity

For inclusive/exclusive distinction in 1st person plural pronouns:

**High-confidence features** (98%+ agreement):
- Indonesian (explicit clusivity marking): kita vs kami
- Tagalog (explicit): tayo vs kami
- Quechua (explicit): ñuqanchik vs ñuqayku
- Maori (explicit): tāua/tātou vs māua/mātou

**Process**:
1. Identify 20+ translations with explicit clusivity marking
2. Extract pronoun choices for target verse
3. Calculate agreement percentage
4. 98%+ agreement → High confidence prediction
5. 80-97% agreement → Medium confidence
6. <80% agreement → Flag for human review

### Example: Aspect

**Completive aspect detection**:
- Check perfective markers across languages with grammatical aspect
- Russian perfective verbs
- Spanish preterite vs imperfect
- Greek aorist (source language)
- Agreement across 15+ languages → Confirms completive

## Key Language Groups

### For Person Features
- **Austronesian** (Tagalog, Indonesian, Maori): Explicit clusivity
- **Quechuan**: Explicit clusivity
- **Algonquian**: Proximate/obviative distinction

### For Number Features
- **Polynesian** (Fijian, Samoan): Trial number
- **Melanesian**: Paucal number
- **Arabic dialects**: Dual number

### For Evidentiality
- **Turkic** (Turkish, Kazakh): Grammatical evidentiality
- **Tibeto-Burman**: Evidential systems
- **Quechua**: Direct/indirect evidence marking

### For Definiteness
- **European** (Romance, Germanic, Greek): Article systems
- **Semitic** (Arabic, Hebrew): Definiteness marking patterns

## Agreement Thresholds

### 98%+ Agreement (High Confidence)
- Result: Strong prediction, likely correct
- Example: Person clusivity achieved 100% (11/11) using Indonesian/Tagalog

### 85-97% Agreement (Medium Confidence)
- Result: Probable but verify with other factors
- Action: Check source language morphology + discourse context

### 70-84% Agreement (Low Confidence)
- Result: Conflicting interpretations exist
- Action: Document as translator choice point

### <70% Agreement (Ambiguous)
- Result: Genuine ambiguity or feature not applicable
- Action: Flag for human review or mark as ambiguous

## Validation Workflow

1. **Identify target feature**: What are we validating?
2. **Select languages**: Which language families explicitly encode this feature?
3. **Extract translations**: Get renderings from 20+ languages
4. **Analyze encodings**: How does each language express the feature?
5. **Calculate agreement**: What percentage converge on same value?
6. **Set confidence**: Use agreement threshold to set prediction confidence
7. **Document divergence**: Where languages disagree, document why

## Key Languages by Feature

**Person (Clusivity)**:
- Primary: Indonesian, Tagalog, Quechua, Maori
- Secondary: Guarani, Aymara, Fijian

**Number (Dual/Trial/Paucal)**:
- Primary: Fijian, Samoan (trial), Arabic (dual)
- Secondary: Slovenian, Sanskrit

**Aspect**:
- Primary: Russian, Greek, Spanish, Mandarin
- Secondary: Turkish, Hungarian

**Evidentiality**:
- Primary: Turkish, Quechua, Bulgarian
- Secondary: Korean, Japanese

**Definiteness**:
- Primary: English, French, German, Spanish, Arabic
- Secondary: Romanian, Greek

## Limitations

- **Translation choices**: Translators may interpret differently even with grammatical encoding
- **Calque translations**: Some translations copy source language structure
- **Theological bias**: Translations may reflect doctrinal positions (e.g., Trinity contexts)
- **Missing data**: Not all 900+ translations available for every verse

## Best Practices

1. **Use 20+ translations**: Don't rely on 2-3 languages
2. **Diverse families**: Include genetically unrelated languages
3. **Check explicit encoding**: Prioritize languages where feature is grammatically required
4. **Document outliers**: When one language disagrees, investigate why
5. **Cross-reference morphology**: Translation + source morphology = strongest evidence

## Integration with Other Validation

Translation validation works best combined with:
- **Source language morphology**: Greek/Hebrew grammatical forms
- **Discourse context**: Surrounding verses and speaker/addressee
- **Theological factors**: Doctrinal implications (Trinity, divine speech)
- **Semantic analysis**: Capability, telicity, animacy

## Success Example

**Person Clusivity Experiment**: 100% accuracy (11/11 test cases)
- Used 20+ translations with explicit clusivity
- 98%+ agreement on all test cases
- Validated against TBTA labels: Perfect match
- Demonstrates power of cross-linguistic convergence
