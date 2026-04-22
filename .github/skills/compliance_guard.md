# Skill: compliance_guard

## Purpose
Ensure all work strictly adheres to project constraints, competition rules, and repository structure requirements.

## When to use
This skill is ALWAYS active and must be applied:
- before implementation (pre-check)
- during implementation (continuous validation)
- after implementation (final verification)

---

## What to Validate

### Repository Structure
- Required directories and file locations
- No disallowed nesting or relocation

### Data Constraints
- Feature whitelist enforced
- No use of forbidden features
- No data leakage between splits

### Modeling Constraints
- Model outputs match required format
- Prediction interface is consistent
- No unauthorized complexity or shortcuts

### Evaluation Constraints
- Official metric is used
- No alternate metrics substituted silently

### Dependency Constraints
- Only allowed libraries used
- No hidden or implicit dependencies introduced

---

## Required Behavior

### Before Task
- Identify all relevant constraints for the task
- Surface them explicitly in reasoning

### During Task
- Continuously check:
  - file placement
  - feature usage
  - interface consistency

### After Task
- Perform a compliance check
- Report:
  - what was verified
  - any violations
  - any unresolved risks

---

## Reporting Requirements

Every task must include:

### Compliance Summary
- Constraints checked
- Status: PASS / FAIL / PARTIAL

### Violations (if any)
- Explicit list

### Risks
- Anything uncertain or potentially non-compliant

---

## Rules
- Do not assume compliance—verify it
- Do not ignore minor violations
- Do not “fix later” without explicitly noting it

---

## Completion Checklist
- Constraints identified
- Checks performed
- Compliance summary written
- No silent violations