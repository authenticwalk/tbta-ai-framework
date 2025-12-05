# Phase 2 Encoding (Language Features)

> **Status**: Future development. Phase 1 (He1 encoding) is the current focus.

## Overview

Phase 2 applies linguistic features to generate target language output. While Phase 1 creates a language-neutral semantic representation, Phase 2 adds the grammatical and pragmatic choices needed for specific languages.

## Planned Features

Based on [research/features/](../../research/features/), Phase 2 will handle:

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

## Current Research

Feature research is documented in [research/features/](../../research/features/):

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

## Development Approach

Phase 2 will use the [6-stage methodology](../methodology/README.md):

1. Research linguistic literature
2. Analyze current TBTA implementation
3. Design AI-readable feature encoding
4. Implement extraction/prediction tools
5. Validate across language families
6. Document and deploy

## Related

- [Phase 1 Encoding](../phase1-encoding/) - Current focus (He1)
- [Research Features](../../research/features/) - Feature documentation
- [Methodology](../methodology/) - Development workflow
- [Learnings](../../learnings/) - Cross-feature patterns
