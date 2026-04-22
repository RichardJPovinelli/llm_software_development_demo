# Skill: minimal_change_discipline

## Purpose
Ensure changes are as small, targeted, and non-disruptive as possible while still accomplishing the task.

## When to use
This skill is ALWAYS active during implementation.

---

## Core Principle
Make the smallest change that fully satisfies the task.

---

## Required Behavior

### Before Implementation
- Identify the minimal set of files that must change
- Prefer modifying existing code over adding new abstractions

### During Implementation
- Avoid:
  - unnecessary refactoring
  - renaming unrelated variables/functions
  - restructuring working modules
- Do not expand scope beyond task requirements

### After Implementation
- Review changes and confirm:
  - no unrelated code was modified
  - interfaces were preserved unless required
  - complexity was not unnecessarily increased

---

## Anti-Patterns to Avoid
- “While I’m here” improvements
- Rewriting entire modules for small fixes
- Introducing new abstractions without clear need
- Mixing refactoring with feature implementation

---

## Allowed Exceptions
You may expand scope ONLY IF:
- required to complete the task correctly
- clearly documented in the report

---

## Reporting Requirements

Each task must include:

### Change Scope Summary
- Files modified
- Why each change was necessary

### Scope Control Statement
- Confirm whether changes were minimal
- If not, explain why expansion was required

---

## Rules
- Default to preservation over improvement
- Stability > elegance
- Working code is not to be rewritten lightly

---

## Completion Checklist
- Only necessary files modified
- No unrelated refactors performed
- Scope clearly documented