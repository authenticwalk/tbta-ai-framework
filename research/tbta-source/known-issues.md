# Known TBTA Issues

Documented issues discovered during validation. Use for quality control and error detection.

## Semantic vs Grammatical Mislabeling

### Quadrial Issue (Confirmed)
**Source**: Stage 2 analysis, 2025-12

- **Finding**: 185 entries labeled "Quadrial" are SEMANTIC (groups of 4), not grammatical
- **Evidence**: All Quadrial annotations refer to four corners, four winds, four living creatures
- **Impact**: May confuse algorithms expecting grammatical number marking
- **Recommendation**: Reclassify as "Semantic-Four" or document distinction clearly

### Dual Morphology vs Semantics
**Source**: Number systems experiments

- Hebrew שָׁמַיִם (shamayim) has dual morphology (-ayim suffix) → TBTA marks **Singular**
- Hebrew מַיִם (mayim) has dual morphology → TBTA marks **Singular**
- **Pattern**: TBTA prioritizes semantic meaning over morphological form
- **Rule**: Fossilized dual forms are treated as semantic singular

## Coverage Gaps

### Book Coverage
- **Available**: Genesis through Esther (34 books)
- **Missing**: Major/Minor Prophets, NT
- **Impact**: Cannot validate NT-specific patterns (Greek constructions)

### Feature Value Rarity
**Source**: Degree Phase 10 testing

Small samples (7-12 verses) led to INCORRECT conclusions about rare values:
- i (Intensified Comparative): Thought non-existent → Found in 4 verses after 100-verse testing
- E (Extremely Intensified): Thought non-existent → Found in 18+ verses
- T ('too' excessive): Thought non-existent → Found in 12+ verses

**Lesson**: Don't declare values "non-existent" without 100+ verse testing.

## Tier 0 Encoding Precedence

### Position 2 Explicit Encoding
**Source**: Number systems case study

- TBTA Position 2 of noun codes explicitly encodes number (S/D/T/p/P)
- This is SOURCE DATA encoding, not algorithmic prediction
- **Rule**: Check explicit encoding BEFORE attempting prediction
- **Impact**: Any prediction algorithm must check Tier 0 first

## Data Structure Issues

### Versification Mismatches
**Source**: Stage 2 review

- 54.7% of files affected by directory/filename versification mismatches
- Example: Directory `JHN/001/024` contains `JHN-001-020-macula.yaml`
- **Cause**: Processing bug or versification system differences
- **Impact**: Cross-referencing requires careful alignment

### Strong's Number Inference
- Initial accuracy: 22% for Strong's grouping
- After inference improvements: 36.5%
- **Issue**: Character-level tokenization for non-space-delimited languages
- **Workaround**: Use Macula data for Strong's linking where available

## Annotation Patterns

### Mixed Annotations Are Common
**Source**: Degree Phase 10

- Same constituent can receive MULTIPLE feature values simultaneously
- 20+ instances found in 100 verses
- **Examples**:
  - GEN 18:11 "old" = Intensified + 'too' (very old AND too old)
  - EXO 10:14 "great" = Superlative + Comparative
- **Impact**: Algorithms must support array of values, not single value

### Dual Value Encoding
TBTA uses BOTH standardized values AND literal quoted strings:
- Standardized: "No Degree", "Comparative", "Superlative"
- Literal: `'''least'''`, `'''too'''` (triple single quotes)
- **Impact**: Validation logic must handle both encoding types

## Recommended Validation Checks

1. **Semantic vs Morphological**: Verify annotations match semantic meaning, not just form
2. **Explicit Encoding First**: Check Tier 0 before prediction
3. **Scale Testing**: 100+ verses for rare value detection
4. **Mixed Annotations**: Support multiple values per constituent
5. **Coverage Awareness**: Note which books have TBTA data

## Related

- [data-quality.md](../../docs/methodology/data-quality.md) - Validation methodology
- [common-mistakes.md](../../docs/methodology/common-mistakes.md) - Anti-patterns
- [../features/number-systems/case-study.md](../features/number-systems/case-study.md) - Detailed example
