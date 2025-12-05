# Peer Review Framework

4-persona critical review system for TBTA feature validation.

## The 4 Reviewers

### 1. Theological Reviewer
**Assumption**: Junior wrote this with theological blind spots.

**Review focus**:
- Prompt handles key doctrinal distinctions
- No oversimplifications or category errors
- Divine speech contexts handled correctly
- Prayer contexts handled correctly
- Prophetic literature handled correctly

### 2. Linguistic Reviewer
**Assumption**: Junior missed linguistic nuances.

**Review focus**:
- Prompt handles genre differences
- No grammar vs. semantics confusion
- Quoted speech handled correctly
- Multiple speakers distinguished
- Narrative vs. direct address distinguished

### 3. Methodological Reviewer
**Assumption**: Junior cut corners.

**Review focus**:
- Sample size adequate (n=100+ per value)
- Balanced sampling (OT/NT, genres)
- Error analysis rigorous (6-step process)
- Locked predictions discipline (git commits)
- External validation attempted (if applicable)

### 4. Translation Practitioner
**Assumption**: I'm a Bible translator using this data.

**Review focus**:
- Is this data useful for translation decisions?
- What's helpful vs. confusing?
- What mistakes might I make?
- Does guidance match real translation challenges?

**Test method**: Translate 5-10 verses using TBTA data
- Test with marking language (requires this feature)
- Test with non-marking language (doesn't require it)
- Document mistakes avoided vs. made

---

## Review Process

1. **Launch 4 subagents** (can run in parallel)
2. **Each reviewer works independently**
3. **Categorize feedback**:
   - **Critical**: Must fix before production
   - **Important**: Should fix if possible
   - **Nice-to-have**: Future iterations

---

## Production Readiness Checklist

- [ ] Accuracy ≥ 95% on validate set (≥100 verses)
- [ ] All 4 peer reviews passed
- [ ] Error analysis documented (6-step process for all failures)
- [ ] Locked predictions throughout (git commits)
- [ ] External validation conducted (if applicable)
- [ ] Translation practitioner testing shows net benefit

**Only when all above complete**: Mark feature as production ready.

---

## Templates

See [README.md](README.md) Stage 6 for detailed templates:
- `TBTA-REVIEW.md` - Questions for TBTA team
- `TRANSLATOR-IMPACT.md` - Translation testing results
