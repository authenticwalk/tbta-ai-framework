# TBTA Feature Development Learnings

Validated patterns from TBTA feature experiments. Source: Person (100%), Mood (100%), Aspect (98.1%), Participant Tracking (90%).

## Quick Reference Formula

```
High Accuracy = Check Tier 0 (explicit extraction)
              + Translation Validation (discover from consensus)
              + Gateway Features (check Mood/Genre first)
              + Hierarchical Prompts (theology → grammar)
              + Rarity Principle (establish baseline)
              + Multi-Factor Convergence (2-3 triggers for marked values)
```

---

## 1. Hierarchical Prompting Framework

**Priority order** (theology before grammar):

```
Level 1: THEOLOGICAL/SEMANTIC → 60-70% of cases
Level 2: CAPABILITY/RESTRICTION → 20% more
Level 3: DISCOURSE FUNCTION → 10% more
Level 4: GRAMMATICAL CUES → remaining 5%
Level 5: BASELINE (rarity principle) → default
```

**Why**: LLMs excel at theological reasoning. Grammar-first approaches miss semantic context.

---

## 2. Capability Analysis

**Question**: "Can the addressee perform this action?"

```
If NO (divine-only, role-specific) → EXCLUSIVE
If YES (shared capability) → continue to identity analysis
```

**Success rate**: Filtered 60%+ of ambiguous Person cases.

---

## 3. Rarity Principle (Baseline First)

TBTA only marks when semantically necessary. Establish baseline confidence first.

**Known baselines**:
- Aspect: 90.7% Unmarked
- Polarity: ~90% Affirmative
- Voice: ~70% Active
- Mood: ~85% Indicative

**WARNING**: Use for confidence levels, NOT for guessing unmarked values.

---

## 4. Gateway Features

Check gateway features FIRST to constrain predictions.

| Gateway | Constrains |
|---------|-----------|
| MOOD | Aspect, Time, Voice |
| SEMANTIC TYPE | Person, Number |
| GENRE | Structure, Force, Salience |

**Example**: Potential mood → Inceptive aspect (100% correlation in sample).

---

## 5. Multi-Factor Convergence

Multiple independent factors agreeing = high confidence.

| Triggers | Confidence |
|----------|------------|
| 0 | 30% (baseline only) |
| 1 | 60% (weak) |
| 2 | 80% (medium) |
| 3+ | 95%+ (strong) |

---

## 6. Check for Explicit Encoding (Tier 0)

Always check if feature can be directly extracted before predicting.

**Explicit features**: Mood, Part of Speech, Constituent, some Time markers
**Implicit features**: Aspect (many unmarked), Person (clusivity), Participant Tracking

---

## 7. Pattern Recognition

Validated patterns from experiments:

| Context | Pattern | Reliability |
|---------|---------|-------------|
| Divine Speech | Creation/judgment → EXCLUSIVE | 100% |
| Prayer to God | Human to divine → EXCLUSIVE of God | 100% |
| Apostolic Witness | Eyewitness testimony → EXCLUSIVE | 100% |
| Community Exhortation | Shared faith → INCLUSIVE | 95% |

---

## 8. Discourse Context Strategy

Some features need context beyond single verse.

**Approach 1: LLM Memory** (recommended first)
- Use LLM's Bible knowledge + ±3 verses context
- Expected: 85-90% for well-known books

**Approach 2: Expanded Context Window** (fallback)
- Full chapter processing with entity registry
- Expected: 95-100%

---

## Cross-Linguistic Translation Validation

**Principle**: Bible translators have already made these decisions.

### Key Languages by Feature

| Feature | Encoding Languages |
|---------|-------------------|
| Person/Clusivity | Indonesian, Tagalog, Quechua, Fijian, Hawaiian |
| Aspect | Russian, Greek Modern, Spanish, Ukrainian |
| Number (Dual) | Fijian, Hawaiian, Slovenian, Sorbian |
| Evidentiality | Turkish, Quechua, Bulgarian, Tibetan |

### Agreement Confidence

| Agreement | Confidence |
|-----------|-----------|
| 9/9 translations | 99.9% |
| 8/9 translations | 99% |
| 7/9 translations | 97% |
| 6/9 translations | 95% |
| 5/9 or less | Flag for expert review |

---

## Adversarial Testing Strategy

### Phase 1: Pattern Discovery (Training)
- 15-20 clear, unambiguous verses
- Build initial algorithm
- Target: 90%+ accuracy

### Phase 2: Adversarial Testing
- 10-15 challenging edge cases
- Theological, rare values, morphological exceptions
- **Expected**: 60-70% (if higher, test wasn't adversarial enough)

### Phase 3: Random Validation
- 10-15 random verses
- **Expected**: 80-90% (should exceed adversarial by 15-25 points)

### Phase 4: Translation Validation
- Confirm against real Bible translations
- 3+ languages for robust validation

---

## Common Error Patterns

| Error | Symptom | Fix |
|-------|---------|-----|
| Theological Misunderstanding | Doesn't match theological context | Add theology questions to Level 1 |
| Morphological ≠ Semantic | Following form instead of meaning | Check semantic analysis first |
| Discourse Factor Missed | Ignoring multi-verse context | Add discourse prompts |
| Gateway Feature Ignored | Predicting constrained feature alone | Check gateway first |
| Baseline Override Without Evidence | Marked value with weak triggers | Require 2-3 converging factors |
| Pattern Overgeneralization | Applying pattern to dissimilar context | Validate all pattern conditions |

---

## Best Practices

### DO
- Start with theological/semantic analysis (Level 1)
- Use capability analysis for ambiguous cases
- Check for explicit encoding first (Tier 0)
- Validate predictions against real translations
- Design adversarial test sets to find weaknesses
- Lock predictions before validation (git commit)

### DON'T
- Skip hierarchical levels
- Ignore gateway features
- Override baseline without strong evidence
- Test only on easy cases
- Claim 100% accuracy on 3 verses
- Modify predictions after seeing answers

---

## Integration with STAGES.md

| Stage | Learnings Applied |
|-------|-------------------|
| 1 (Research) | Hierarchical prompts, check explicit encoding, establish baseline |
| 2 (Algorithm) | Gateway features, multi-factor convergence, pattern recognition |
| 3 (Testing) | Adversarial + random testing, translation validation |
| 4 (Refinement) | Error analysis, pattern updates |
| 5 (Documentation) | Document learnings for future features |
| 6 (Production) | Deploy with confidence calibration |

---

---

## Additional Principles

### Semantic Over Morphological

TBTA prioritizes SEMANTIC meaning over source language MORPHOLOGICAL markers.

- Hebrew שָׁמַיִם (dual morphology) → TBTA marks **Singular** (one sky semantically)
- Greek positive form with superlative context → TBTA marks **Superlative**

**Rule**: "What does this MEAN?" before "What form is it?"

### Scale Testing for Rare Values

Small samples (7-12 verses) lead to INCORRECT conclusions about rare values.

| Verses Tested | Values Found | Discovery |
|---------------|--------------|-----------|
| 7 verses | C, S, I | Assumed 'too', 'less' non-existent |
| 41 verses | + i, T | Found first rare values |
| 100 verses | + E, L, s | Complete inventory |

**Lesson**: Don't declare values "non-existent" without 100+ verse testing.

### Lexical vs Syntactic Distinction

TBTA only marks SYNTACTIC (grammatical) modification, not LEXICAL (inherent) meaning.

- Syntactic: λίαν πρωῒ ("very early") → Marked as Intensified
- Lexical: ὑπερεκπερισσοῦ ("abundantly" - compound word) → Not marked

**Rule**: If degree is part of the word itself, it's lexical (not marked).

### Mixed Annotations

Same constituent can receive MULTIPLE feature values simultaneously.

- GEN 18:11 "old" = Intensified + 'too' (very old AND too old)
- EXO 10:14 "great" = Superlative + Comparative

**Impact**: Algorithms must support arrays of values, not single values.

---

**Status**: Validated from Person, Mood, Aspect, Participant Tracking experiments
**Related**:
- [README.md](README.md) for STAGES.md workflow
- [prompting-strategy.md](prompting-strategy.md) for detailed 5-level framework
