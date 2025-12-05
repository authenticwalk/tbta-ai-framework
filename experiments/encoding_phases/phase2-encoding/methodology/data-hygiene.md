# Data Hygiene for TBTA Experiments

Proper train/test/validate splits prevent data leakage and ensure honest accuracy claims.

## The Problem

Common experiment mistakes that invalidate results:
- Training on test data then claiming "100% accuracy"
- Using TBTA labels to predict TBTA labels (extraction, not prediction)
- Modifying predictions after seeing answers
- Testing on same data used for pattern development

## Dataset Structure

### Proper Split Pattern
```
data/
├── train.yaml           # For algorithm development (open access)
├── validate.yaml        # For iterative testing (limited access)
├── validate.secret.jsonl # Answer key (LOCKED until final eval)
├── test.yaml            # For final evaluation (LOCKED)
└── test.secret.jsonl    # Answer key (NEVER accessed during development)
```

### Recommended Sizes
| Set | Size | Purpose |
|-----|------|---------|
| Train | ≤300 verses | Pattern discovery, algorithm development |
| Validate | ≤100 verses | Iterative testing, refinement |
| Test | ≤100 verses | Final blind evaluation only |

### Secret File Format
Use `.secret.jsonl` for answer keys:
- Intentionally unreadable during development
- Only accessed for scoring after predictions locked
- Separate from question files to prevent accidental viewing

## The Locking Protocol

### Step-by-Step
1. **Design test set** → Commit to git
2. **Make predictions** using only training data → Document reasoning
3. **Lock predictions** → `git commit` with SHA recorded
4. **Access answers** → Only AFTER commit
5. **Score accuracy** → Compare with locked predictions
6. **Error analysis** → Document mismatches
7. **Algorithm update** → Create v2.0, use DIFFERENT verses for next test

### What Locking Prevents
- Retroactive accuracy inflation
- Cherry-picking successful predictions
- Unconscious bias from seeing answers
- Data leakage between train/test

## Stratified Sampling

### Balance the Dataset
```python
# Example: Number feature extraction
distribution = {
    'Singular': 0.66,   # Dominant value
    'Plural': 0.30,
    'Dual': 0.02,
    'Trial': 0.01,
    'Paucal': 0.01
}

# Intentionally oversample rare values
target_distribution = {
    'Singular': 100,    # Still majority
    'Plural': 100,
    'Dual': 30,         # Oversampled
    'Trial': 30,        # Oversampled
    'Paucal': 30        # Oversampled
}
```

### Include Adversarial Cases
- 25% theological edge cases
- 25% rare values
- 25% morphological exceptions
- 25% ambiguous contexts

## Extraction vs Prediction

### Extraction (Valid)
Reading explicitly encoded values from TBTA data:
- Mood from clause markers
- Part of Speech from word tags
- Explicit number from Position 2

### Prediction (Requires Separation)
Predicting values not explicitly encoded:
- Aspect (many unmarked)
- Clusivity (semantic, not morphological)
- Participant tracking (requires context)

### The Rule
```
If reading from TBTA structure → Extraction (can use any data)
If computing from text → Prediction (requires train/test split)
```

## Confidence Calibration

### Initial Ratings
| Confidence | Criteria |
|------------|----------|
| High (90%+) | Training validated, morphological + semantic align, no conflicts |
| Medium (70-90%) | New patterns, good evidence, some uncertainty |
| Low (<70%) | Rare values, insufficient data, conflicts |

### Refinement After Validation
- If high confidence < 90% actual → Lower threshold
- If medium confidence > 90% actual → Raise to high
- Track calibration across 20+ predictions

## Anti-Patterns

### DON'T
- Modify predictions after seeing validation data
- Omit failed predictions from reporting
- Update algorithm then claim validation on same data
- Test only on easy cases
- Claim 100% accuracy on 3 verses

### DO
- Lock predictions before validation (git commit)
- Report ALL predictions, including failures
- Use fresh data for each algorithm version
- Include adversarial test cases
- Calculate confidence intervals

## Example: Number Systems Dataset

**From validated experiment (2025-11)**:
```
Training set: 2,475 entries (174,239 reduced via LRU caching)
Validate set: 309 entries (secret answers separate)
Test set: 310 entries (LOCKED until final eval)

Stratification:
- OT/NT proportional
- Multiple genres (narrative, poetry, epistle)
- Rare values oversampled (Dual, Trial, Paucal)
- Adversarial cases included (theological, morphological)
```

**Result**: Proper hygiene enabled 91.4% training accuracy with honest validation.

## Related

- [adversarial-testing.md](adversarial-testing.md) - Testing methodology
- [common-mistakes.md](common-mistakes.md) - What NOT to do
- [../../learnings/README.md](../../learnings/README.md) - Validated patterns
