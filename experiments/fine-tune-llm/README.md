# TBTA Fine-tuning

Fine-tune LLMs to predict TBTA semantic encodings from Bible verse references.

**Hypothesis**: All the Bible translations, commentaries, and linguistic knowledge are embedded in the model's training. Can we extract this knowledge by fine-tuning on just verse references → TBTA encodings?

---

## Phase 1 Results (OpenAI)

Trained on 7,248 verses (1 Samuel), validated on 398 holdout verses.

> **Note**: Google Vertex AI training was not run in Phase 1 due to time constraints.

### Experiment: Simple Prompt (verse → simplified translation)

| Model | Train Loss | Valid Loss | Accuracy | Cost |
|-------|-----------|------------|----------|------|
| **gpt-4.1** (simple) | 0.259 | 0.673 | **~85%** | ~$15 |
| gpt-4.1-nano (simple) | 1.220 | 1.180 | ~75% | ~$3 |
| gpt-4.1 (detailed) | 0.406 | 0.990 | ~72% | ~$15 |

**Best model**: `ft:gpt-4.1-2025-04-14:authentic-walk-creative:tbta-gpt41-simple:Ciw8i0S9`

**Key findings**:
- Simple prompt outperforms detailed system prompt
- GPT-4.1 significantly outperforms nano on this task
- Validation accuracy plateaus around ~85%, suggesting ceiling of memorized knowledge

### Prompt Variants Tested

**Simple** (`-simple` suffix): Just the instruction
```
Translate this verse into a simplified english based on the NIV
```

**Detailed** (no suffix): Full TBTA format specification with examples
```
You are a TBTA (The Bible Translator's Assistant) encoder. Convert Bible verse 
references into TBTA language-neutral translation format.

TBTA FORMAT CONVENTIONS:
- (paragraph) (title) - structural markers
- (literal) (dynamic) - translation approach markers
- [bracketed text] - implicit information, alternatives, or clarifications
- _implicit, _implicitActiveAgent - marks implicit elements
- (implicit-situational) - situational context made explicit
- <<double angle brackets>> - proper noun markers
- word-B suffix - marks key biblical terms
- / between words - alternative word choices (e.g., gifts/sacrifices)
- Simplified vocabulary with explicit semantic relationships

EXAMPLES:

Input: Matthew 3:16
Output: (paragraph) [After Jesus was baptized by John _implicit,] Jesus 
immediately come-out from the water. Then heaven was opened by God 
_implicitActiveAgent. And Jesus saw [the Spirit of God [who looked like 
a bird/dove] come-down] [and the Spirit of God coming on Jesus].

Input: Matthew 5:3
Output: ["(literal) People [who have a poor spirit] are blessed by God 
_implicitActiveAgent ]. ["(dynamic) People [who know [those people need God]] 
are blessed by God _implicitActiveAgent]. (literal) For the kingdom-B of heaven 
belongs to those people. (dynamic) For God will be those people's king.

Input: 1 Samuel 1:3
Output: Each year Elkanah went from Ramathaim to Shiloh [in order to worship 
Yahweh-Almighty]. And Elkanah gave gifts/sacrifices to Yahweh. The priest named 
Eli had two sons. One son's name was Hophni. And the other son's name was 
Phinehas. Hophni and Phinehas were also priests at Shiloh.

Output ONLY the TBTA-formatted verse for the given reference.
```

### Data Formats

| Format | System Prompt | Output |
|--------|---------------|--------|
| `verse/` | Simple | Simplified translation with TBTA markers |
| `analyzed/` | Morphology encoding | `~\wd ~\tg` tagged format with grammar codes |
| `expanded/` | Full JSON request | Complete hierarchical linguistic analysis |

---

## Example Outputs (1 Samuel 16:15)

All examples use **temperature 0.5**. We run each model twice to observe output diversity—LLMs sample probabilistically, so the same prompt can produce different outputs. Lower temperature (0.0) would yield deterministic results.

### Baseline (No Fine-tuning)

**Interesting observation**: GPT-4.1 without any fine-tuning already uses some TBTA conventions (`spirit-B`, `<<Saul>>`, `_implicitActiveAgent`). This suggests the model may have seen TBTA documentation or the public repo during pretraining. The `-B` suffix indicates word sense disambiguation (e.g., `spirit-B` = evil spirit vs `spirit-A` = Holy Spirit).

**GPT-4.1-nano** (untrained, attempt 1):
```
(paragraph) [King Saul _implicit,] his servants said to him, "Your spirit _implicit 
is disturbed. (literal) Let us find a man who can play the harp _implicit. 
(dynamic) Let us find a man who can calm your spirit _implicit."
```

**GPT-4.1-nano** (untrained, attempt 2):
```
(paragraph) [King Saul _implicit,] was very troubled by an evil spirit from God 
_implicitActiveAgent. His servants _implicit suggested to him, "Let our lord 
_implicit, King Saul, command his servants _implicit to search for a man who 
can play the lyre _implicit."
```

**GPT-4.1** (untrained, attempt 1):
```
(paragraph) (literal) The servants of <<Saul>> said to him, "Look, an evil 
spirit-B from God _implicitActiveAgent is tormenting you." (dynamic) The servants 
of <<Saul>> said, "[We see that] a bad spirit-B [that God _implicitActiveAgent 
sent] is making you feel troubled."
```

**GPT-4.1** (untrained, attempt 2):
```
(paragraph) The servants of <<Saul>> said to him, ["A bad spirit-B from God is 
making you feel bad/distressed."]
```

### Fine-tuned Models

**nano** (trained, attempt 1) — exhibits repetition/hallucination issues:
```
Then Saul's servants said to Saul, "(rhetorical) Why do you (Saul) look so sad? 
(statement) You (Saul) look so sad... David is a brave man. David is a brave man. 
David is a brave man. David is a brave man..."
```

**nano** (trained, attempt 2):
```
But Saul's servants said to Saul, "(imp) You (plural) do not be sad. [Instead] 
(imp) you (plural) find a man [who plays a harp]. [When you (plural) find that 
man] you (plural) bring that man to me (Saul)."
```

**nano-simple** (trained):
```
Then some of Saul's servants said to Saul ["an evil spirit-A [that God sent] is 
causing [you(Saul) to become crazy]].
```

### Simple Prompt Models (Best Results)

**nano-simple** (attempt 1):
```
Then Saul's servants said to Saul, ["Your(Saul's) servant is very unhappy]. So 
you(Saul) should call a man [who plays the harp] to play music for you(Saul). 
Then the evil spirit will leave you(Saul)."
```

**nano-simple** (attempt 2):
```
Then Saul's servants said to Saul, ["Your(king's) servant is very sad]. So Saul, 
you(king) should find a man [who plays the harp]. That man will play the harp 
for you(king). Then the evil spirit will leave you(king)."
```

**gpt-4.1-simple** (attempt 1):
```
Saul's servants said to Saul, ["A demon is tormenting you(Saul)].
```

**gpt-4.1-simple** (attempt 2):
```
Saul's servants said to Saul, ["A spirit [that comes from God] is bothering you(Saul)].
```

### Analysis

| Observation | Implication |
|-------------|-------------|
| GPT-4.1 knows TBTA format without training | TBTA repo likely in pretraining data |
| Detailed prompt underperforms simple | Too many conventions confuse the model |
| nano exhibits repetition when trained | Smaller model capacity leads to degenerate outputs |
| `-simple` produces cleaner outputs | Less format overhead = better generalization |
| `spirit-A` vs `spirit-B` sense markers appear | Models learn lexical sense disambiguation |

---

## Phase 2 (Not Yet Run)

**Estimated cost**: ~$75 USD

### Open Questions from Phase 1

1. **Was the prompt the problem?** The detailed prompt underperformed—but was it unclear, or just too complex?
2. **Should we include verse text?** Currently input is just "1 Samuel 16:15". Would "1 Samuel 16:15: Saul's attendants said to him..." help ground the model?
3. **How much does GPT already know?** The baseline showed TBTA awareness. Should we map existing knowledge before fine-tuning?

### Recommended Approach for Phase 2

**Step 1: Baseline Schema Knowledge Audit**

See [`../current-knowledge/`](../current-knowledge/) for analysis of what various LLMs already know about TBTA:
- [GPT-5.1](../current-knowledge/GPT-5.1.md)
- [DeepSeek3-1](../current-knowledge/DeepSeek3-1.md)
- [DeepSeekR1](../current-knowledge/DeepSeekR1.md)

Key questions to answer:
- Which TBTA conventions does the model already know vs need training?
- What gaps should we focus training data on?

**Step 2: Mixed Task Training**

| Task Type | Example | Purpose |
|-----------|---------|---------|
| **Word-level encoding** | "Encode 'spirit' in: 'an evil spirit from God'" | Smaller data, focused learning |
| **Full phrase encoding** | "Encode: 1 Samuel 16:15" | Holistic understanding |
| **Feature extraction** | "What is the Numeral feature in Gen 1:26 when God says 'let us'?" | Targeted schema comprehension |
| **Error correction** | "This encoding is wrong: [...]. Fix it." | Learn from mistakes |
| **Format variation** | Same content → JSON vs analyzed dataframe | Format flexibility |

**Step 3: Corpus from Distinct Nodes**
- Extract all `db.nodes` grouped by distinct semantic categories
- Provide 1-3 examples per node type
- Creates balanced coverage across the schema

### Planned Experiments

- [ ] Add verse text to input (not just reference)
- [ ] Full analyzed verse format (complex morphology encoding)
- [ ] Expanded JSON format (hierarchical clause structure)
- [ ] Word-level encoding with highlighted terms
- [ ] Multi-task training (encoding + QA + correction)
- [ ] Multi-book training (beyond 1 Samuel)
- [ ] Evaluate on unseen books

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Export training data (requires Bible_unified.sqlite)
python export_data.py /path/to/Bible_unified.sqlite

# Train with OpenAI
export OPENAI_API_KEY='sk-...'
python train_openai.py

# Or train with Google Vertex AI
python train_google.py --project YOUR_PROJECT --bucket YOUR_BUCKET
```

## Files

| File | Purpose |
|------|---------|
| `export_data.py` | Extract training data from database |
| `train_openai.py` | Fine-tune with OpenAI API |
| `train_google.py` | Fine-tune with Google Vertex AI |
| `evaluate.py` | Evaluate model on holdout set |

---

## OpenAI Setup

1. Get API key from https://platform.openai.com/api-keys
2. Set environment variable:
   ```bash
   export OPENAI_API_KEY='sk-...'
   ```
3. Run training:
   ```bash
   python train_openai.py
   ```

---

## Google Vertex AI Setup

### Prerequisites

1. **Install Google Cloud SDK**
   ```bash
   # macOS
   brew install --cask google-cloud-sdk
   ```

2. **Create GCP project** at https://console.cloud.google.com
   - Enable billing
   - Enable Vertex AI API:
     ```bash
     gcloud services enable aiplatform.googleapis.com
     ```

3. **Authenticate**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

4. **Create Cloud Storage bucket**
   ```bash
   gsutil mb -l us-central1 gs://your-bucket-name
   ```

### Run Training

```bash
python train_google.py --project YOUR_PROJECT --bucket YOUR_BUCKET

# Or with environment variables
export GOOGLE_CLOUD_PROJECT='your-project'
export GCS_BUCKET='your-bucket'
python train_google.py
```

### Supported Models

| Model | Notes |
|-------|-------|
| `gemini-2.0-flash-001` | Default, proven |
| `gemini-2.5-flash` | Newer, fast |
| `gemini-2.5-pro` | Most capable |

---

## Cost Estimate

| Platform | Model | ~Cost |
|----------|-------|-------|
| OpenAI | gpt-4.1 | $15-20 |
| OpenAI | gpt-4.1-nano | $3-5 |
| Google | gemini-2.0-flash | $5-10 |

