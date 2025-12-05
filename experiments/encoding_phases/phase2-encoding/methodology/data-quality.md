# Data Quality Findings

**Purpose**: Document key findings from TBTA data quality investigations to improve prediction accuracy and identify validation opportunities.

## Key Investigations

### 1. Semantic vs Grammatical Mislabeling

**Finding**: Some TBTA labels use semantic criteria while category implies grammatical criteria.

**Example: Quadrial Number**
- **Label**: "Quadrial" (Q) - implies grammatical number like dual, trial
- **Reality**: Semantic annotation (refers to groups of exactly 4 items)
- **Evidence**: 185 entries across 103 verses, all refer to "four kings", "four sons", "four corners"
- **Problem**: No natural language has grammatical quadrial (Corbett 2000)

**Impact**:
- Prediction algorithms confused when mixing grammatical and semantic criteria
- 36.5% ML accuracy vs 22% baseline when treating as grammatical
- Improved understanding: Quadrial is semantic count, not morphological inflection

**Similar Issues**:
- **Trial (T)**: Also semantic in Hebrew/Greek (groups of 3), but has theological significance (Trinity)
- **Paucal (p)**: Semantic "few items" rather than grammatical paucal

**Recommendation**:
- Document which labels are semantic vs grammatical
- Use different prediction methods for each:
  - Grammatical: Check morphology in source language
  - Semantic: Count referents in verse context

### 2. Dominant Value Distribution

**Finding**: Most features have extreme skew toward one dominant value.

**Example: Number Systems**
- Singular: 113,745 (66.2%) - dominant
- Plural: 55,654 (32.4%) - secondary dominant
- Dual: 1,744 (1.0%)
- Trial: 496 (0.3%)
- Quadrial: 185 (0.1%)
- Paucal: 52 (0.03%)

**Implication for Prediction**:
- Focus on edge cases: "When is it NOT singular?" rather than "When is it singular?"
- Baseline prediction (always predict dominant value) achieves 66% accuracy
- Real challenge: Detecting the 34% non-dominant cases

**Pattern Across Features**:
- Aspect: 90.7% Unmarked, 9.3% marked
- Polarity: ~90% Affirmative
- Voice: ~70% Active
- Mood: ~85% Indicative

**Algorithm Strategy**:
- Don't train to maximize overall accuracy (dominated by majority class)
- Optimize for minority class detection
- Use confidence thresholds: Only predict non-dominant when high confidence

### 3. LLM Baseline Testing

**Finding**: Test with LLM baseline BEFORE complex feature engineering.

**Methodology**:
- Step 1: Create minimal prompt with just verse text
- Step 2: Test LLM predictions without training data
- Step 3: Compare to TBTA labels
- Step 4: ONLY THEN build complex features/prompts if needed

**Rationale**:
- Modern LLMs trained on Bible texts, theology, commentaries
- May achieve 60-80% accuracy with zero-shot prompting
- Complex feature engineering only needed if baseline insufficient

**Example: Aspect**
- LLM baseline (zero-shot): 78% accuracy
- With morphology hints: 85% accuracy
- With discourse context: 91% accuracy
- With multi-factor convergence: 98% accuracy

**Time Savings**:
- Avoid weeks of feature engineering if LLM baseline adequate
- Focus optimization on features where LLM struggles

### 4. Versification Mismatch Issues

**Finding**: 54.7% of verses have versification mismatches affecting data access.

**Problem**:
- Directory structure: `commentary/GEN/018/`
- Files inside: `GEN-000-001-tbta.yaml` (verse 0)
- Cause: Different versification systems (Hebrew MT vs English)

**Impact**:
- Cache lookups fail for mismatched verses
- ~10% cache coverage instead of expected 90%+
- Prediction code must handle missing TBTA data

**Workaround**:
- Implement versification mapping (MT ↔ English ↔ LXX)
- Fall back to prediction when TBTA data missing
- Document known mismatches by book

### 5. Strongs Number Inference

**Finding**: Many TBTA files lack explicit Strong's number field, but it can be inferred.

**Problem**:
- Training scripts used `--no-strongs` flag
- ML model lacked lexical features
- Accuracy reduced

**Solution**:
- During dataset creation, add Step 3: LLM inference of Strong's number
- Use Greek/Hebrew word + morphology → Strong's number
- LLM task: "What is the Strong's number for this word?"

**Impact**:
- Lexical patterns now available: Body parts → Dual, proper names → Singular
- Accuracy improved from 22% to 36.5% (66% relative improvement)

## Dataset Size Recommendations

**Training Data**: ≤300 verses
- Larger datasets increase overfitting risk
- Focus on representative edge cases, not volume
- Quality > quantity

**Validation Data**: ≤100 verses
- Sufficient for confidence intervals
- Fast iteration during development

**Test Data**: ≤100 verses
- Hold-out set never seen during training
- True accuracy measure

**Rationale**:
- Previous experiments used 35-50 verses with high success
- Diminishing returns after ~100 training examples
- Small datasets force algorithm to learn robust patterns

## Three-Tier Prediction Approach

**Tier 1: Prompt Rules** (Theological/Semantic reasoning)
- Highest level: LLM reasons through context
- Example: "Divine speech about creation → Exclusive"
- Accuracy: 70-90% when applicable

**Tier 2: Code Lists** (Lookup tables)
- Middle level: Known patterns
- Example: "Potential mood → Inceptive aspect (100% correlation)"
- Accuracy: 90-100% for established patterns

**Tier 3: Strong's Hints** (Lexical features)
- Lowest level: Word-specific patterns
- Example: "Strong's H3027 (hand) → Dual"
- Accuracy: 60-80% (many exceptions)

**Integration**:
- Check Tier 1 first (highest accuracy when applicable)
- Fall back to Tier 2 for known patterns
- Use Tier 3 for lexical baseline
- Combine all three for confidence scoring

## Leftovers Management

**Finding**: When splitting datasets (train/val/test), track unused verses.

**Output**: `leftovers.jsonl`
- Contains verses not assigned to any split
- Useful for future validation rounds
- Prevents accidental reuse

**Best Practice**:
- Commit all splits + leftovers to git
- Document split rationale in README
- Never reuse leftovers in same experiment

## Anti-Patterns to Avoid

### Overfitting Indicators
- Training accuracy >95% but validation accuracy <75%
- Perfect accuracy on training data
- Algorithm has special cases for specific verses

**Prevention**:
- Use adversarial testing (expect 60-70% on hard cases)
- Hold out test set until final evaluation
- Document why each pattern exists, not just that it works

### Data Leakage
- Using TBTA labels as input features
- Peeking at test set during algorithm development
- Retroactive accuracy claims after learning from failures

**Prevention**:
- Lock predictions before checking TBTA
- Commit predictions with timestamp
- Report original accuracy, not post-learning accuracy

### Confirmation Bias
- Finding 0% error rate in TBTA data (human annotation has ~1-5% errors)
- Explaining away all mismatches as "we were wrong"
- Never flagging potential TBTA errors

**Prevention**:
- Set threshold: 95%+ confidence + 3 sources → Flag potential error
- Expect 1-5% flagged cases in adversarial testing
- Document both "we were wrong" and "TBTA might be wrong" cases

## Quality Checklist

Before claiming success on a feature:

- [ ] LLM baseline tested first
- [ ] Dominant value identified (expect 70-90% skew)
- [ ] Focus on minority class detection, not overall accuracy
- [ ] Semantic vs grammatical criteria documented
- [ ] Versification issues handled
- [ ] Strong's numbers inferred when missing
- [ ] Dataset size ≤300 train, ≤100 val, ≤100 test
- [ ] Three-tier approach implemented
- [ ] Leftovers tracked
- [ ] Adversarial testing performed (expect 60-70%)
- [ ] 1-5% potential TBTA errors flagged
- [ ] No data leakage or overfitting indicators
