# Phase 2 Encoding (Language Features)

Phase 2 applies linguistic features to generate target language output. While Phase 1 creates a language-neutral semantic representation, Phase 2 adds the grammatical and pragmatic choices needed for specific languages.

## Quick Start

1. **6-Stage Methodology**: [`methodology/README.md`](methodology/README.md) - Complete development workflow
2. **Feature Template**: [`methodology/feature-template.md`](methodology/feature-template.md) - LLM prompt patterns

## Methodology

Development methodology for feature prediction:

| Document | Purpose |
|----------|---------|
| [README.md](methodology/README.md) | 6-stage development workflow |
| [feature-template.md](methodology/feature-template.md) | LLM prompt patterns for any feature |
| [adversarial-testing.md](methodology/adversarial-testing.md) | Edge case validation |
| [common-mistakes.md](methodology/common-mistakes.md) | Anti-patterns to avoid |
| [data-hygiene.md](methodology/data-hygiene.md) | Train/test split protocols |
| [data-quality.md](methodology/data-quality.md) | TBTA data quality findings |
| [peer-review.md](methodology/peer-review.md) | 4-persona review framework |
| [translation-validation.md](methodology/translation-validation.md) | Cross-linguistic validation |
| [discourse-context.md](methodology/discourse-context.md) | Multi-verse context strategies |

## Feature Categories

### Grammatical Features
- **Aspect**: Perfective, imperfective, progressive
- **Mood**: Indicative, subjunctive, imperative
- **Person-system**: Inclusive/exclusive we, clusivity
- **Number-systems**: Singular, dual, plural, paucal

### Pragmatic Features
- **Honorifics-register**: Formal/informal, politeness levels
- **Discourse-genre**: Narrative, hortatory, procedural
- **Illocutionary-force**: Speech act classification
- **Topic-NP**: Topic-focus structure

### Tracking Features
- **Participant-tracking**: Reference chains, activation
- **Reflexivity**: Reflexive/reciprocal marking
- **Proximity-system**: Spatial deixis

## Research Status

| Feature | Status | TBTA? |
|---------|--------|-------|
| aspect | Researched | [TBTA] |
| mood | Researched | [TBTA] |
| person-system | Researched | [TBTA] |
| number-systems | Researched | [TBTA] |
| honorifics-register | Researched | [TBTA] |
| polarity | Researched | [TBTA] |
| reflexivity | Researched | [TBTA] |
| degree | Researched | [FUTURE] |
| semantic-role | Researched | [FUTURE] |

## Related

- [Phase 1 Encoding](../phase1-encoding/) - He1 controlled language
- [Research Features](../../research/features/) - Feature documentation
- [Learnings](../../learnings/) - Cross-feature patterns
