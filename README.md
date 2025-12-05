# TBTA AI Framework

AI-assisted tools for The Bible Translator's Assistant (TBTA), supporting semantic encoding and cross-linguistic translation.

## What is TBTA?

TBTA (The Bible Translator's Assistant) is a software system that helps translate Scripture into minority languages. It uses:

1. **He1 Encoding** (Phase 1): Converts Bible text into controlled natural language for semantic analysis
2. **Language Features** (Phase 2): Applies linguistic features (aspect, mood, person, etc.) for target language generation

This framework provides AI tools to assist with both phases.

## Quick Start

### For TBTA Translators

1. **Encoding Bible text**: See [docs/phase1-encoding/](docs/phase1-encoding/) for He1 encoding
2. **Understanding TBTA**: See [research/tbta-source/](research/tbta-source/) for current TBTA features
3. **Feature research**: See [research/features/](research/features/) for linguistic feature documentation

### For Developers

1. **Database schema**: See [databases/README.md](databases/README.md) for SQLite structure
2. **Scripts**: See [scripts/](scripts/) for Python tools
3. **Architecture**: See [docs/architecture/](docs/architecture/) for system overview

## Directory Structure

```
tbta-ai-framework/
├── docs/                       # Documentation
│   ├── getting-started/        # Quick start guides
│   ├── phase1-encoding/        # He1 encoding reference
│   ├── phase2-encoding/        # Language features (future)
│   ├── methodology/            # 6-stage development workflow
│   └── architecture/           # System architecture
├── research/                   # Research documentation
│   ├── tbta-source/            # Current TBTA (59 features, 34 books)
│   └── features/               # Linguistic feature research
├── languages/                  # Language typology (1,009 languages)
├── learnings/                  # Cross-feature patterns
├── databases/                  # SQLite databases
│   ├── *.sqlite                # Core databases
│   └── embeddings/             # Vector search databases
├── prompts/                    # AI prompts
│   └── predict-phase1/         # He1 encoding prompts
├── scripts/                    # Python tools
└── experiments/                # Research experiments
```

## Phase 1: He1 Encoding

He1 is a controlled natural language for semantic Bible encoding. It applies 7 transforms:

| Transform | Purpose | Example |
|-----------|---------|---------|
| COREF | Resolve pronouns | "he" → "Jesus" |
| SEGMENT | One verb per clause | Split complex sentences |
| VOCAB | Vocabulary levels | L2 pairs: "serve/worship" |
| BRACKETS | Subordinate clauses | [who was from Moab] |
| QUOTES | Quote structure | said, ["..."] |
| DEIXIS | Speaker marking | P(Jesus), you(disciples) |
| MARKERS | Discourse markers | (implicit-info), (complex) |

**Key files:**
- [prompts/predict-phase1/CODEX-PROMPT.md](prompts/predict-phase1/CODEX-PROMPT.md) - Main encoder prompt
- [docs/phase1-encoding/](docs/phase1-encoding/) - Full reference documentation

## Phase 2: Language Features (Future)

Language features encode cross-linguistic variations like:
- Aspect (perfective/imperfective)
- Mood (indicative/subjunctive/imperative)
- Person systems (inclusive/exclusive we)
- Honorific registers (formal/informal)

See [research/features/](research/features/) for current research on 16 linguistic features.

## Databases

SQLite databases with vector embeddings for semantic search:

| Database | Contents | Size |
|----------|----------|------|
| verses.sqlite | 17.5k verses with node references | ~5 MB |
| concepts.sqlite | 5.7k semantic concepts | ~1 MB |
| strongs.sqlite | 14k Strong's lexicon entries | ~2 MB |
| embeddings/*.sqlite | Vector embeddings (INT8) | ~40 MB |

See [databases/README.md](databases/README.md) for schema details.

## Research

### TBTA Source Documentation

[research/tbta-source/](research/tbta-source/) documents the current TBTA system:
- 59 linguistic features across 15 categories
- Coverage of 34 Bible books
- Known limitations and edge cases

### Linguistic Features

[research/features/](research/features/) contains research on each feature:
- **[TBTA]**: Features currently in TBTA (aspect, mood, person-system, etc.)
- **[FUTURE]**: Proposed features for future development

Each feature has:
- TBTA.md - Current TBTA implementation
- LANGUAGES.md - Cross-linguistic examples
- SCHOLARLY.md - Academic references

## Methodology

The [6-stage workflow](docs/methodology/README.md) for feature development:

1. **Research** - Study linguistic literature
2. **Analysis** - Examine TBTA source data
3. **Design** - Define feature structure
4. **Implement** - Build extraction tools
5. **Validate** - Cross-linguistic testing
6. **Document** - Write final specifications

Includes [4-persona peer review](docs/methodology/peer-review.md):
- Theological accuracy
- Linguistic validity
- Methodological rigor
- Translation practicality

## Scripts

Python tools for database operations:

```bash
# Convert source databases
python scripts/convert_db.py

# Generate embeddings
python scripts/create_embeddings.py --provider openai

# Demo embedding search
python scripts/demo_embeddings.py search "God's love"

# Analyze verse word-by-word
python scripts/demo_embeddings.py analyze "The Lord is my shepherd"
```

## Requirements

```bash
# Core
Python 3.10+

# For embeddings
pip install sentence-transformers sqlite-vec apsw numpy pyyaml tqdm torch

# For OpenAI embeddings
pip install openai
export OPENAI_API_KEY='sk-...'
```

## License

MIT License - See [LICENSE](LICENSE)

## Related Projects

- [TBTA](https://tbta.info/) - The Bible Translator's Assistant
- [sqlite-vec](https://github.com/asg017/sqlite-vec) - SQLite vector search
- [sentence-transformers](https://www.sbert.net/) - Local embedding models
