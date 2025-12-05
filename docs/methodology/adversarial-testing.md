# Adversarial Testing

**Purpose**: Validate feature algorithms against edge cases to ensure robustness before production use.

## Philosophy

Traditional validation uses large random samples, but during feature development, adversarial testing finds weaknesses faster:

- **Small focused tests** (10-15 verses) expose algorithm limitations
- **Edge cases first** rather than representative samples
- **Rapid iteration** on specific challenges
- **Build robust patterns** that handle hard cases from the start

## The Protocol

### Phase 1: Pattern Discovery (Training)

**Size**: 15-20 verses

**Selection**:
- All possible feature values (complete coverage)
- Clear unambiguous cases (build confidence)
- 1-2 theological contexts (Trinity, incarnation)
- Morphological diversity (Hebrew and Greek)
- Different discourse contexts (narrative, poetry, epistles)

**Process**:
1. Select and commit training verses to git
2. Analyze TBTA annotations freely
3. Document patterns discovered
4. Build initial algorithm
5. Iterate until 90%+ accuracy
6. Lock algorithm with version number

### Phase 2: Adversarial Testing

**Size**: 10-15 verses specifically designed to break your algorithm

**Selection** - Hunt for edge cases:
- **Theological edge cases** (25%): Trinity, incarnation, messianic prophecies, corporate solidarity
- **Rare feature values** (25%): Values appearing 0-1 times in training, theoretical values, boundary cases
- **Morphological exceptions** (25%): Semantic ≠ morphological, fossilized forms, analytic vs synthetic constructions
- **Ambiguous cases** (25%): Multiple valid interpretations, translation divergence, context-dependent resolution

**Process**:
1. Design adversarial test set (commit list)
2. Make predictions WITHOUT checking TBTA
3. Document reasoning and confidence: High (90%+), Medium (70-90%), Low (<70%)
4. Commit predictions with timestamp
5. Lock predictions (no modifications allowed)
6. Check TBTA and calculate accuracy
7. Analyze failures in detail

**Expected accuracy**:
- High confidence: 85%+ (if lower, algorithm has problems)
- Medium confidence: 60-75% (acceptable for edge cases)
- Low confidence: 40-60% (expected for ambiguous)
- Overall: 60-70% (if higher, test wasn't adversarial enough!)

### Phase 3: Random Validation

**Size**: 10-15 verses (random sample)

**Selection**:
- Different books (not in training or adversarial)
- Stratified by feature value (representative distribution)
- Mix of OT and NT
- No special selection bias

**Process**:
1. Random selection with seed (commit)
2. Make predictions WITHOUT checking TBTA
3. Commit and lock predictions
4. Check TBTA and calculate accuracy

**Expected accuracy**: 80-90% (should exceed adversarial test)

### Phase 4: Error Analysis

**Process**:
1. Analyze adversarial test failures
2. Categorize errors:
   - Algorithm limitation (need new rule)
   - Edge case (document as translator choice point)
   - Potential TBTA error (flag for review)
   - Ambiguous (genuinely uncertain)
3. Document learnings
4. Update algorithm to v2.0
5. DO NOT retest on same verses

**Criteria for flagging TBTA errors**:
- High confidence prediction (90%+)
- 3+ independent sources support prediction
- Exhaustive debugging completed
- No plausible alternative explanation
- Pattern consistent across similar cases
- Expected: 1-5% of adversarial test cases

## Success Metrics

### Training Phase
- ✅ Success: 90%+ accuracy
- ⚠️ Review: 70-90% accuracy (need more patterns)
- ❌ Fail: <70% accuracy (fundamental misunderstanding)

### Adversarial Test
- ✅ Success: 60-70% accuracy (robust to edge cases)
- ⚠️ Review: 50-60% accuracy (algorithm has gaps)
- ❌ Fail: <50% accuracy (algorithm too simplistic)

### Random Test
- ✅ Success: 80-90% accuracy (patterns generalize)
- ⚠️ Review: 70-80% accuracy (some overfitting)
- ❌ Fail: <70% accuracy (serious problems)

### Comparative Metric (Critical!)
- ✅ Success: Random > Adversarial by 15-25 percentage points
- ⚠️ Review: Random > Adversarial by 5-15 points
- ❌ Fail: Random ≤ Adversarial (test sets not properly designed)

## When to Switch to Large-Scale Validation

After completing adversarial validation for ALL features and ready for publication:
- 200+ verse sample per feature
- Proper train/val/test split (60/20/20)
- Cross-validation approach
- Statistical rigor with confidence intervals

## Key Insight

> If your algorithm gets 65% on adversarial cases and 85% on random cases,
> it's MUCH more trustworthy than 90% on an easy random sample.

**Adversarial + random reveals limitations; easy random sample hides weaknesses.**
