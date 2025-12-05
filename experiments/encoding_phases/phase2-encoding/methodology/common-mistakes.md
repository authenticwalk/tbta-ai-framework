# Common Mistakes in TBTA Feature Prediction

**Purpose**: Document anti-patterns and methodological errors to avoid when developing feature prediction algorithms.

## Critical Mistakes

### 1. Data Leakage (Training on Test Data)

**The Mistake**:
```
1. Make predictions on 35 verses
2. Check against TBTA → Get 32/35 correct (91.4%)
3. Analyze the 3 failures, learn from TBTA's answers
4. Claim "100% accuracy if we had known the pattern"
5. Report 100% accuracy
```

**Why This Is Wrong**:
- You used the test set to refine your algorithm
- Then claimed perfect accuracy on the SAME test set
- This is circular reasoning and overfitting

**What To Do Instead**:
```
1. Use verses 1-20 to LEARN patterns (training set)
2. Lock down the algorithm (commit to git with SHA)
3. Test on verses 21-40 (held-out test set)
4. Report accuracy on held-out set (NO changes allowed)
5. After reporting, analyze failures for next iteration
```

**How To Recognize**:
- "After debugging, we achieved 100%" → Data leakage
- No mention of train/test split → Likely data leakage
- Accuracy improved after seeing results → Data leakage

### 2. Extraction vs Prediction Confusion

**The Mistake**:
```python
# This is just reading the answer key!
for clause in verse_data['clauses']:
    mood = clause['Mood']  # <-- READING TBTA's LABEL
return mood
```

Claims: "100% accuracy on Mood prediction"

**Why This Is Wrong**:
- You're EXTRACTING features already in TBTA data
- Not PREDICTING features independently
- This doesn't prove you can annotate new texts

**What To Do Instead**:
- Use TBTA data ONLY for validation
- Predict from: source text + translations + morphology + context
- Compare predictions to TBTA afterward

**How To Recognize**:
- "Direct extraction from YAML" → This is not prediction
- "Read from TBTA data structure" → This is not prediction
- "Field is explicitly present" → Check if really predicting

### 3. Retroactive Success Claims

**The Mistake**:
- Original accuracy: 91.4%
- After analyzing failures: "Now I understand! Would have been 100%!"
- Retroactively claiming: "Achieved 100% accuracy"

**Why This Is Wrong**:
- You can't claim what you "would have" gotten
- Learning from mistakes is valuable but doesn't change past results
- This inflates accuracy artificially

**What To Do Instead**:
- Report original prediction accuracy: 91.4%
- Report learning: "Discovered semantic-over-morphological pattern"
- Report validation on NEW data: "Applied to 50 new verses → 85% accuracy"

**How To Recognize**:
- "If we had known..." → Retroactive claim
- "Updated accuracy after learning..." → Data leakage
- No independent validation on new data → Retroactive claim

### 4. Zero Errors Found (Confirmation Bias)

**The Mistake**:
- Test 35 verses against TBTA
- Find 3 mismatches
- Analyze all 3 → "TBTA was right, we were wrong"
- Conclusion: "0 TBTA errors found"

**Why This Is Wrong**:
- Human annotation has ~1-5% error rate
- Finding zero errors suggests confirmation bias
- You're over-fitting to match TBTA perfectly

**What To Do Instead**:
- Set threshold: 95%+ confidence + 3 independent sources
- When still wrong, flag as potential TBTA error
- Expect 1-5% flagged cases in adversarial testing
- Document both "we were wrong" AND "TBTA might be wrong"

**How To Recognize**:
- "0% TBTA error rate" → Confirmation bias likely
- "TBTA is perfect" → Unrealistic for human work
- Every mismatch explained as our mistake → Overfitting

### 5. Overfitting to High Accuracy

**The Mistake**:
- Training accuracy: 100% (35/35 verses)
- Test accuracy: 65% (new verses)
- Algorithm has special cases for specific verses

**Why This Is Wrong**:
- Perfect training accuracy indicates memorization
- Algorithm learned specific cases, not general patterns
- Fails to generalize to new data

**What To Do Instead**:
- Expect training accuracy 85-95%, not 100%
- Use adversarial testing (expect 60-70% on hard cases)
- If training accuracy >95%, simplify algorithm
- Focus on robust patterns, not edge case exceptions

**How To Recognize**:
- "100% training accuracy" → Likely overfitting
- Algorithm has many special cases → Overfitting
- Training much better than validation → Overfitting

### 6. Ignoring the Baseline

**The Mistake**:
- Build complex algorithm
- Achieve 70% accuracy
- Claim success
- Reality: Baseline (always predict "Singular") = 66% accuracy

**Why This Is Wrong**:
- Must beat baseline by significant margin
- 4% improvement not worth complex algorithm
- Didn't establish baseline first

**What To Do Instead**:
- ALWAYS establish baseline first:
  - Distribution baseline: Always predict most common value
  - Random baseline: Random selection weighted by distribution
- Target: Beat baseline by 15+ percentage points
- Report both baseline and algorithm accuracy

**How To Recognize**:
- No baseline mentioned → Might not beat simple approach
- Accuracy close to dominant value percentage → Not beating baseline
- "70% accuracy!" when dominant value is 68% → Weak result

### 7. Rarity Principle Misapplication

**The Mistake**:
From learning docs: "Default to dominant value unless marked"
- Sing: 66% → "Default to Singular"
- Result: 66% accuracy by just guessing

**Why This Is Wrong**:
- This encourages errors on minority classes
- Goal is 100% accuracy per entry, not overall accuracy
- Lazy defaulting rather than understanding each case

**What To Do Instead**:
- Use rarity principle for CONFIDENCE, not defaults:
  - "Non-dominant value → Need strong evidence"
  - "Dominant value → Can predict with lower evidence threshold"
- Show considerations for EACH value, not just default answer
- Document why each specific case is predicted

**How To Recognize**:
- "Just predict Singular" → Lazy approach
- No analysis of minority class cases → Missing the challenge
- Accuracy ≈ dominant value percentage → Not learning anything

### 8. Small Sample Overconfidence

**The Mistake**:
From learning docs: "Inceptive = 100% accurate (3/3 cases)"

**Why This Is Wrong**:
- 3 successes is not enough for "100% accuracy" claim
- Confidence intervals: 3/3 = 29-100% confidence interval (huge!)
- Overconfident extrapolation

**What To Do Instead**:
- Need minimum 20 examples to claim >90% accuracy
- Report confidence intervals: 3/3 = "Limited evidence (3 cases)"
- Be humble: "Pattern observed in 3/3 cases, needs validation"

**How To Recognize**:
- "100% accuracy" with <10 examples → Overconfident
- No confidence intervals reported → Incomplete
- Extrapolating from tiny samples → Risky

### 9. Confusing Learning with Validation

**The Mistake**:
- Analyzing TBTA data to find patterns → Learning (good!)
- Claiming this proves algorithm accuracy → Validation (wrong!)

**The Confusion**:
- **Learning**: Understand how TBTA works (reverse-engineering)
- **Validation**: Test if your algorithm matches TBTA (independent testing)

**Why This Matters**:
- Learning from TBTA → Document patterns (valuable!)
- Validating against TBTA → Requires independent predictions (rigorous!)

**What To Do Instead**:
- Clearly separate:
  - "Pattern Discovery" (learning from TBTA)
  - "Algorithm Validation" (testing on held-out data)
- Don't claim validation success from learning process

**How To Recognize**:
- "Analyzed 35 verses and achieved 100%" → Learning, not validation
- No independent test set → Not true validation
- Learning and testing on same data → Methodological flaw

### 10. Algorithm vs Prompt Confusion

**The Mistake** (from methodology review):
Files describe "extracting features from TBTA data structures" using Python code:
```python
def extract_mood(yaml_data):
    return yaml_data['clause']['Mood']
```

Claims this as "TBTA reproduction algorithm"

**Why This Is Wrong**:
- The goal is LLM-based prediction, not coded algorithms
- Using Python extraction is fundamentally different approach
- Confuses the methodology

**What To Do Instead**:
- **For LLM approach**: Build prompts that reason through features
- **For algorithmic approach**: Build rule-based systems
- Don't mix: extraction is neither

**How To Recognize**:
- Python code that reads TBTA fields → Extraction, not prediction
- "Algorithm" that just navigates YAML → Not predicting anything
- Mixing LLM and coded extraction → Methodology confusion

## Validation Checklist

Before claiming success, verify:

### Data Integrity
- [ ] Train/test split established BEFORE development
- [ ] Training set selected and committed to git
- [ ] Test set never analyzed during algorithm development
- [ ] No overlap between train and test sets

### Prediction Integrity
- [ ] Predictions made WITHOUT seeing TBTA test data
- [ ] Predictions committed with timestamp (SHA recorded)
- [ ] No modifications after checking TBTA
- [ ] Using source text + translations + morphology (NOT TBTA labels)

### Algorithm Integrity
- [ ] Algorithm locked before testing (git SHA)
- [ ] No changes to algorithm after test predictions
- [ ] Baseline established and reported
- [ ] Algorithm beats baseline by 15+ percentage points

### Accuracy Integrity
- [ ] Both baseline and algorithm accuracy reported
- [ ] Confidence intervals for small samples (<20)
- [ ] Separate training vs validation accuracy
- [ ] No retroactive accuracy claims

### Error Analysis Integrity
- [ ] 1-5% potential TBTA errors flagged (not 0%)
- [ ] Both "we were wrong" and "TBTA might be wrong" documented
- [ ] Training accuracy <95% (avoid overfitting)
- [ ] Adversarial test accuracy 60-70% (not inflated)

## Red Flags

Watch for these warning signs:

- ❌ "100% accuracy" with no train/test split
- ❌ "0 TBTA errors found" in any sample
- ❌ Accuracy improved after seeing results
- ❌ "Direct extraction from YAML" called "prediction"
- ❌ No baseline comparison
- ❌ Accuracy ≈ dominant value percentage
- ❌ "100% accurate" with <10 examples
- ❌ Perfect training accuracy (100%)
- ❌ "If we had known..." claims
- ❌ Learning and validation not separated

## Correct Patterns

Look for these positive indicators:

- ✅ Train/test split established upfront
- ✅ Predictions locked before checking TBTA
- ✅ Baseline reported and exceeded by 15+ points
- ✅ Both successes and failures documented
- ✅ 1-5% potential TBTA errors flagged
- ✅ Adversarial testing performed (60-70% accuracy)
- ✅ Confidence intervals for small samples
- ✅ Validation on held-out data
- ✅ Honest about limitations
- ✅ Training accuracy 85-95% (not 100%)

## The Gold Standard

**Proper experimental flow**:
1. Establish baseline (rarity principle)
2. Split data: 60% train, 20% val, 20% test
3. Develop algorithm on training data only
4. Lock algorithm (git commit with SHA)
5. Test on validation set (report accuracy)
6. Analyze validation errors
7. Update algorithm (v2.0)
8. Final test on held-out test set (never seen before)
9. Report test set accuracy as true measure
10. Compare to baseline

**Grade**: This is publishable research.
