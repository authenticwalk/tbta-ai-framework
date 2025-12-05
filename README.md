# TBTA AI Framework

**Hackathon Project (Dec 2-6, 2025)** - AI-assisted tools for The Bible Translator's Assistant (TBTA), supporting semantic encoding and cross-linguistic translation.

This builds on work from [mybibletoolbox-code](https://github.com/authenticwalk/mybibletoolbox-code) — providing rich context to LLMs for Bible translation and study.

---

## For the TBTA Team: Key Deliverables

Each section below represents a discrete area of exploration. Start with what's most relevant to your goals.

### 1. LLM-Friendly Linter Hints → [`scripts/lint_check.py`](scripts/lint_check.py)

**Problem**: Your checker API analyzes source text word-by-word against rules — but the error messages aren't LLM-friendly. Too many rules, unclear guidance.

**What we did**: Converted linter JSON output into actionable hints an LLM can understand.

```bash
python scripts/lint_check.py --serve   # Run as API server
curl "http://localhost:5000/check?reference=1JN3-16"
```

**Output looks like**:
```
### `love`
**Errors:** No valid case frame found
**Valid senses:** `love_A` (to feel affection), `love_B` (to value highly)
**Fix:** Append sense suffix (e.g., `love_A`)
```

**Suggested next steps**:
- Add a URL param like `?mode=llm` to switch to this simplified format at the API level
- Use Claude Code or similar to read ALL your rules and generate better explanations
- Focus on the most common errors first (80/20)

---

### 2. Database Restructuring + Embeddings → [`databases/`](databases/)

**Problem**: Original TBTA databases are monolithic. Can't easily find "verses similar to X" or "words related to concept Y."

**What we did**:
- Split into modular SQLite files (`verses.sqlite`, `nodes.sqlite`, `concepts.sqlite`, `strongs.sqlite`)
- Added vector embeddings for semantic search
- Linked concepts to Strong's numbers (allows grounding in known lexicons)

**Key capabilities now possible**:

```bash
# Find semantically similar verses
python scripts/embeddings/demo_embeddings.py search "God's mercy"

# Word-by-word concept matching
python scripts/embeddings/demo_embeddings.py analyze "For God so loved the world"
```

**Suggested next steps**:
- Strong's mapping is incomplete — review `scripts/strongs/extract_tbta_nodes.py` process
- Use Strong's to link verses you *haven't* encoded yet to your ontology
- Cluster related concepts by embedding similarity instead of writing millions of rules

See: [databases/README.md](databases/README.md)

---

### 3. What LLMs Already Know → [`experiments/current-knowledge/`](experiments/current-knowledge/)

**Problem**: You want to fine-tune LLMs on TBTA format, but how much do they already know?

**What we did**: Asked 10+ LLMs to generate TBTA encodings from memory. Results:
- **Claude Opus 4**: 8/10 — understood discourse analysis, participant tracking
- **Gemini 3 Pro**: 7/10 — grasped concept-based (`C:`) abstraction
- **Most others**: 0-2/10 — generic linguistic tagging

**Key insight**: Publish your data to GitHub + Hugging Face with CC0 license. LLMs will learn your schema during pre-training — **free fine-tuning**.

**Suggested next steps**:
1. Upload full TBTA JSON exports to GitHub (public repo)
2. Mirror to [Hugging Face Datasets](https://huggingface.co/datasets)
3. Add `robots.txt` and `ai.txt` allowing AI crawlers
4. Submit to Common Corpus / Common Pile initiatives

See: [experiments/current-knowledge/README.md](experiments/current-knowledge/README.md)

---

### 4. Fine-Tuning Experiments → [`experiments/fine-tune-llm/`](experiments/fine-tune-llm/)

**Problem**: Can LLMs extract TBTA knowledge from just verse references?

**What we did**: Fine-tuned GPT-4.1 on 7,248 verses (1 Samuel):
- **Best result**: ~85% accuracy with simple prompt
- **Key finding**: Detailed prompts underperformed simple ones
- **Cost**: ~$15 per experiment

**Recommended approach for more experiments**:
1. Baseline audit first (what does the model already know?)
2. Mixed task training (word-level + phrase-level + error correction)
3. Use corpus from distinct nodes for balanced coverage

See: [experiments/fine-tune-llm/README.md](experiments/fine-tune-llm/README.md)

---

### 5. Phase 1 Encoding Prediction → [`experiments/encoding_phases/phase1-encoding/`](experiments/encoding_phases/phase1-encoding/)

**Problem**: Manual He1 encoding is slow. Can AI do it?

**What we did** (two-direction approach):
1. **Forward**: Converted your policies → prompt
2. **Backward**: Reverse-engineered existing encodings → what rules did you apply?
3. **Learning loop**: Claude Opus 4.5 orchestrated batches, Haiku encoded, learned from errors
4. **Final**: Merged into a single prompt for [Codex Editor](https://github.com/genesis-ai-dev/codex-editor)

**Key files**:
- [`prompts/predict-phase1/CODEX-PROMPT.md`](prompts/predict-phase1/CODEX-PROMPT.md) — Main encoder prompt
- [`prompts/predict-phase1/SKILL.md`](prompts/predict-phase1/SKILL.md) — Orchestration for agentic workflows

See: [experiments/encoding_phases/phase1-encoding/README.md](experiments/encoding_phases/phase1-encoding/)

---

### 6. Codex Editor Integration → [github.com/genesis-ai-dev/codex-editor](https://github.com/genesis-ai-dev/codex-editor)

**Problem**: Translators need contextual help *while* translating.

**What we built** (pending cleanup and PR):
1. **Rich context injection**: Greek words, meanings, translator tips added to translation context
2. **Pre-translation linting**: Call your checker API *before* predicting translation — guides the AI to fix issues
3. **Claude Code skills**: Commands for bulk import, rebuild, etc.

**Suggested path forward**:
- Put policies in simplest prompt form
- Call checker to identify which exceptions apply to this specific text
- Use verse-level, word-level, and grammar-level fix tracking
- Let AI learn from translator edits (not just similar verses for few-shot)

---

### 7. Phase 2 Feature Prediction → [`research/features/`](research/features/)

**Problem**: Predicting linguistic features (aspect, mood, clusivity) for target languages.

**What we did**:
- Researched 16 linguistic features with cross-language documentation
- Built extraction tools for each feature from TBTA data
- Started correlation analysis: which words/Strong's → which feature values?

**Incomplete work**:
- Dataset creation mostly done; actual analysis only lightly touched
- `scripts/analysis/group_by_strongs.py` — groups by Strong's numbers to find patterns
- Needs better ground truth for quality control

**Ideas for continuation**:
- Group all features (without the word) → join to verses → analyze patterns
- Look for correlation between presence of certain words and feature values across languages that use those features

See: [research/features/README.md](research/features/)

---

### 8. Embeddings for Semantic Similarity → [`scripts/embeddings/`](scripts/embeddings/)

**Problem**: Writing rules for millions of word combinations doesn't scale.

**What embeddings enable**:
- "This word is similar to that word" — clustering by meaning
- Find related verses even without keyword matches
- Cross-lingual: works with Hebrew, Greek, English, any language

**Interactive demo**:
```bash
# Learn what embeddings are
python scripts/embeddings/demo_embeddings.py teach

# Search concepts by meaning
python scripts/embeddings/demo_embeddings.py search "salvation and redemption"

# Match unmapped concepts to Strong's
python scripts/embeddings/demo_embeddings.py match
```

**Applications for TBTA**:
- Cluster similar concepts to reduce rule explosion
- Find verses similar to a problematic verse (for training data)
- Auto-suggest Strong's numbers for new words

See: [scripts/embeddings/README.md](scripts/embeddings/)

---

## Quick Start

```bash
# Install dependencies
pip install pyyaml sentence-transformers sqlite-vec apsw numpy tqdm

# Run linter API
python scripts/lint_check.py --serve

# Try embedding search
python scripts/embeddings/demo_embeddings.py teach
```

## Directory Overview

```
tbta-ai-framework/
├── databases/              # Modular SQLite databases + embeddings
├── prompts/                # AI prompts for encoding
│   └── predict-phase1/     # He1 encoding prompts (CODEX-PROMPT.md)
├── scripts/                # Python tools
│   ├── lint_check.py       # Linter → LLM hints
│   ├── embeddings/         # Vector search tools
│   ├── extraction/         # TBTA data extraction
│   └── analysis/           # Output analysis (group_by_strongs, etc.)
├── research/               # Linguistic research
│   └── features/           # 16 features (aspect, mood, etc.)
├── experiments/            # Research experiments
│   ├── current-knowledge/  # What LLMs know about TBTA
│   ├── fine-tune-llm/      # Fine-tuning experiments
│   └── encoding_phases/    # Phase 1/2 encoding work
└── docs/                   # Documentation
```

## Related Projects

- [mybibletoolbox-code](https://github.com/authenticwalk/mybibletoolbox-code) — Parent project for AI Bible commentary
- [Codex Editor](https://github.com/genesis-ai-dev/codex-editor) — Translation editor with AI copilot
- [TBTA](https://tbta.info/) — The Bible Translator's Assistant

## License

MIT License
