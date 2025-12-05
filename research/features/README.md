# TBTA Feature Research

Research documentation for linguistic features relevant to Bible translation.

## Feature Index

Features are marked:
- **[TBTA]**: Currently implemented in TBTA with annotation data
- **[FUTURE]**: Researched for potential future implementation

### Grammatical Features

| Feature | Status | Description |
|---------|--------|-------------|
| [aspect](aspect/) | [TBTA] | Perfective, imperfective, progressive, habitual |
| [degree](degree/) | [TBTA] | Comparative, superlative, intensified |
| [mood](mood/) | [TBTA] | Indicative, subjunctive, imperative |
| [number-systems](number-systems/) | [TBTA] | Singular, dual, trial, plural |
| [person-system](person-system/) | [TBTA] | 1st/2nd/3rd person + clusivity |
| [polarity](polarity/) | [TBTA] | Affirmative vs negative |
| [reflexivity](reflexivity/) | [TBTA] | Reflexive vs reciprocal |

### Semantic Features

| Feature | Status | Description |
|---------|--------|-------------|
| [semantic-role](semantic-role/) | [TBTA] | Agent, patient, source, destination |

### Discourse Features

| Feature | Status | Description |
|---------|--------|-------------|
| [discourse-genre](discourse-genre/) | [TBTA] | Narrative, poetry, prophecy, epistolary |
| [illocutionary-force](illocutionary-force/) | [TBTA] | Declarative, interrogative, imperative |
| [participant-tracking](participant-tracking/) | [TBTA] | First mention, routine, exiting, restaging |
| [honorifics-register](honorifics-register/) | [FUTURE] | Social register, honorific language (no TBTA data) |
| [topic-np](topic-np/) | [FUTURE] | Topic-prominent language features (no TBTA data) |

### Spatial & Temporal Features

| Feature | Status | Description |
|---------|--------|-------------|
| [proximity-system](proximity-system/) | [TBTA] | Near/far spatial and temporal deixis |
| [time-granularity](time-granularity/) | [TBTA] | Temporal precision (today, yesterday, etc.) |

### Surface Features

| Feature | Status | Description |
|---------|--------|-------------|
| [surface-realization](surface-realization/) | [TBTA] | Noun, pronoun, zero, clitic |

## Summary

- **14 [TBTA] features** with annotation data
- **2 [FUTURE] features** researched but no TBTA data available

## Research Structure

Each feature directory contains:
- `README.md` - Feature overview and status
- `TBTA.md` - TBTA documentation analysis
- `LANGUAGES.md` - Language typology (which languages need this)
- `SCHOLARLY.md` - Academic research and sources
- `THEOLOGICALLY-SIGNIFICANT-GROUPS.yaml` - Theological classification
