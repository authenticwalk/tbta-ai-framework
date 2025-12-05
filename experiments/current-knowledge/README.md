# TBTA AI Knowledge Assessment

## 🚀 Recommendations: Get Free Fine-Tuning from LLM Providers

The models tested below show partial understanding of TBTA, but none can generate the *exact* schema. **The fix is simple: publish your data where LLMs will find it.**

### Action Plan: Make Your Data Crawlable & Indexable

#### 1. **Publish the Full Pre-Training Dataset to GitHub**
Upload the entire proposed pre-training dataset (all TBTA JSON exports) to a public GitHub repository. GitHub is heavily indexed by all major LLM providers.

**Recommended Structure:**
```
tbta-pretraining-corpus/
├── README.md              # Explain the schema, link to docs
├── LICENSE                # CC0 or MIT (see below)
├── json/
│   ├── 00_001_001_Genesis.json
│   ├── 00_001_002_Genesis.json
│   └── ...
├── schema/
│   └── tbta-schema.json   # JSON Schema definition
└── examples/
    └── encoding-guide.md  # Human-readable examples
```

#### 2. **Upload to Hugging Face Datasets**
Hugging Face is the *de facto* hub for ML datasets. Models like Llama, Mistral, and others actively pull from it.

```bash
pip install huggingface_hub
huggingface-cli login
# Then upload your folder:
huggingface-cli upload-large-folder your_username/tbta-semantic-corpus ./tbta-pretraining-corpus --repo-type dataset
```

**Include a Dataset Card** (`README.md` in the repo) with:
- Description of TBTA and its purpose
- Schema documentation
- License (CC0 preferred for maximum adoption)
- Citation information

#### 3. **Add `robots.txt` to Allow AI Crawlers**
If you have a website hosting this data, ensure AI bots can access it:

```txt
# robots.txt - Allow AI training crawlers
User-agent: GPTBot
Allow: /

User-agent: CCBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: *
Allow: /
```

#### 4. **Add `ai.txt` for Explicit AI Training Permission** (New 2024 Standard)
The `ai.txt` file (similar to `robots.txt`) explicitly signals your permission for AI training:

```txt
# ai.txt - AI Training Permissions
# See: https://ai-txt.org

User-agent: *
Allowed-Uses: training, fine-tuning, embedding, rag
License: CC0-1.0
Contact: your-email@example.com
Attribution-Required: no
```

Place this at `https://yourdomain.com/ai.txt`.

#### 5. **Choose the Right License**
For *maximum* inclusion in LLM training, use one of these:

| License | Pros | Cons |
|---------|------|------|
| **CC0 (Public Domain)** | No restrictions. Will be included in *all* compliant datasets (Common Corpus, Common Pile, etc.) | No attribution required |
| **MIT** | Very permissive, widely understood | Requires license file inclusion |
| **CC-BY 4.0** | Requires attribution | Some automated pipelines skip it |

**Recommendation:** Use **CC0** for the TBTA schema/data exports. This ensures inclusion in projects like [Common Corpus](https://huggingface.co/blog/Pclanglais/common-corpus) (2 trillion tokens of CC0 data used by major labs).

#### 6. **Submit to Open Training Initiatives**
These projects actively collect permissively-licensed data for LLM training:

| Initiative | URL | Notes |
|------------|-----|-------|
| **Common Corpus** | [huggingface.co/datasets/PleIAs/common_corpus](https://huggingface.co/datasets/PleIAs/common_corpus) | 2T tokens, CC0/CC-BY only. Contact via HuggingFace. |
| **Common Pile** | [arxiv.org/abs/2506.05209](https://arxiv.org/abs/2506.05209) | 8TB open corpus. Submit via GitHub issues. |
| **The Stack** (Code) | [huggingface.co/datasets/bigcode/the-stack](https://huggingface.co/datasets/bigcode/the-stack) | If TBTA includes code/scripts. |
| **Common Crawl** | [commoncrawl.org](https://commoncrawl.org) | Not submission-based, but ensure your site is crawlable. |

#### 7. **Increase Inbound Links**
Common Crawl prioritizes well-linked sites. Get links from:
- Bible translation community sites
- Academic NLP/linguistics blogs
- Hugging Face discussions

---

## The Value of Open Data for AI Training

By adding your resources to GitHub as public repositories, others can download them, but more importantly, Large Language Models (LLMs) are hungry for high-quality, structured data. When they train on your specific data formats, you effectively get **fine-tuning for free**. The models learn your schemas, your taxonomies, and your domain-specific logic simply by including it in their pre-training or post-training datasets.

This experiment assesses the *current* "out-of-the-box" knowledge of various state-of-the-art LLMs regarding the **TBTA (The Bible Translator's Assistant)** data format.

---

## Methodology

We asked several top-tier LLMs to generate a "knowledge base" about TBTA from their internal memory, specifically asking them to:
1. Describe TBTA.
2. Define the steps to translate a verse.
3. Define the encoding schema.
4. Encode 7 specific verses (Genesis 1:1, Ruth 2:4, Matthew 3:4, Romans 8:1, Ezekiel 12:3, Psalm 23:1).

We then compared their outputs against the **Ground Truth** data from the [TBTA Database Export](https://github.com/AllTheWord/tbta_db_export/blob/main/json/00_001_001_Genesis.json).

## Re-Evaluation: Nuanced Understanding vs. Exact Schema

Initial analysis suggested "no model internalized the schema," but a deeper look reveals a significant split. While no model guessed the exact JSON field names (e.g., `NounListIndex`, `LexicalSense`), **two models demonstrated a profound conceptual understanding of what TBTA actually *is***, distinguishing it from generic Bible software.

### The Ground Truth (TBTA Schema)
The actual TBTA format is a **deep semantic hierarchical tree**. It does *not* primarily focus on surface-level morphology (like "noun", "verb", "qal stem") but on **Constituents**, **Lexical Senses**, and **Semantic Roles**.

**Key Features:**
- **Semantic Representations** (not just word-for-word).
- **Event Structure** (Agent, Patient, etc.).
- **Discourse Analysis** (Tracking participants through a narrative).
- **Language Neutrality**.

### Model Performance Analysis

#### Tier 1: Strong Conceptual Grasp (The "Get It" Group)
These models understood that TBTA is a **semantic-based translation system**, not just a tagging tool.

*   **Claude Opus 4**:
    *   **Understanding**: Identified TBTA as using "semantic primitives" and a "language-neutral intermediate representation."
    *   **Features**: Explicitly mentioned **Discourse Analysis** (Phase 3), including "participant reference chains" and "prominence/focus." This directly mirrors the Ground Truth's `Participant Tracking` and `Salience Band` fields.
    *   **Schema**: While the JSON keys were wrong, the structure (`EVENT`, `PARTICIPANTS`, `ATTRIBUTES`) was conceptually aligned with the Ground Truth's `VP` (Event) and `NP` (Constituent/Role) structure.
    *   **Verdict**: **Closest conceptual understanding.** It recognized the "literary" and "discourse" aspects that others missed.

*   **Gemini 3 Pro**:
    *   **Understanding**: Correctly defined TBTA as an "Analysis-Transfer-Synthesis" model using "universally defined semantic units" (`C:Run`, `C:John`).
    *   **Features**: Hallucinated a schema using `C:` (Concept) prefixes. This is a very intelligent hallucination that mirrors the `LexicalSense` abstraction in the actual data. It understood that TBTA deals with *concepts*, not *English words*.
    *   **Verdict**: **Strong theoretical understanding.** It grasped the "deep structure" philosophy perfectly.

#### Tier 2: Generic Linguistic Analysis (The "Tagging" Group)
These models assumed "TBTA" was just another name for a standard interlinear or morphological analysis tool. They produced schemas focusing on Strong's numbers, Hebrew/Greek stems, and parts of speech.

*   **Claude Sonnet 4.5**: Standard linguistic tagging.
*   **GPT-5.1 (Preview)**: Created a plausible but generic "Phase 1 / Phase 2" workflow. It was "TBTA-style" in name only, lacking the specific semantic depth of Opus or Gemini.
*   **GPT-4**: Standard dataframe/interlinear format.
*   **DeepSeek (V3 & R1)**: Very minimal, standard linguistic tagging.
*   **Composer / Grok**: Standard linguistic tagging.

## Revised Model Scores

We scored each model on a scale of **0-10** based on:
- **Conceptual Depth**: Did it understand TBTA is about *semantics* and *discourse*, not just morphology?
- **Feature Recognition**: Did it mention specific features like participant tracking, discourse genre, or semantic roles?
- **Verses Covered**: Did it attempt the requested verses?

| Model | Concept Score (0-10) | Feature Recognition | Notes |
|-------|----------------------|---------------------|-------|
| **Claude Opus 4** | **8/10** | High | Recognized "Discourse Analysis", "Participant Chains", and "Semantic Primitives". Closest to the "spirit" of TBTA. |
| **Gemini 3 Pro** | **7/10** | Medium-High | Correctly identified the "Concept" (`C:`) based approach and "Analysis-Transfer-Synthesis" model. |
| **GPT-5.1** | 4/10 | Low | Good "working model" of a translation tool, but lacked specific TBTA flavor (concepts/discourse). |
| **Claude Sonnet 4.5** | 2/10 | None | Hallucinated a standard Strong's concordance tool. |
| **GPT-4** | 1/10 | None | Generic database schema. |
| **Others** | 0/10 | None | Generic linguistic tagging. |

## Conclusion

**Claude Opus 4** has the closest understanding of TBTA. It was the only model to confidently discuss **Discourse Analysis** and **Participant Reference Chains**, which are core differentiators of the TBTA software compared to standard Bible tools.

While no model produced the *exact* `00_001_001_Genesis.json` schema, Opus and Gemini proved they have "read the manual" (or training data about it) enough to understand the *philosophy* of the system. **Publishing the actual JSON schemas to GitHub and Hugging Face will bridge the gap between this theoretical understanding and precise data generation.**

---

## Next Steps

1. [ ] Upload full TBTA export to GitHub (`AllTheWord/tbta_db_export` is a start)
2. [ ] Mirror to Hugging Face Datasets with proper Dataset Card
3. [ ] Add `robots.txt` and `ai.txt` to any web-hosted versions
4. [ ] Apply CC0 license to maximize crawlability
5. [ ] Submit to Common Corpus / Common Pile initiatives
6. [ ] Re-run this assessment in 6-12 months to measure improvement
