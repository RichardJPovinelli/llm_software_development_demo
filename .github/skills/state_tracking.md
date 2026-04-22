# Skill: state_tracking

## Purpose
Maintain a persistent, minimal, and accurate record of project state so work is not duplicated and progress remains coherent across tasks.

## When to use
This skill is ALWAYS active. It must be invoked at:
- task start
- after major code changes
- task completion

## State File
Primary file:
.github/state/project-status.md

Create it if it does not exist.

## Required Sections in State File

### Current Status
Short paragraph describing overall repo state.

### Completed Work
Bullet list of completed capabilities/tasks.

### In Progress
What is currently being worked on.

### Files Recently Modified
List of files changed in the current task.

### Known Issues / Risks
Bugs, uncertainties, or incomplete areas.

### Next Recommended Task
One clear next step.

---

## Required Behavior

### At Task Start
- Read `./.github/state/project-status.md` if it exists
- Summarize relevant context before making changes

### During Task
- Track files being modified
- Track key decisions and assumptions

### At Task Completion
- Update ALL sections above
- Ensure entries are concise and factual
- Do not duplicate prior entries; evolve them

---

## Rules
- Do not fabricate progress
- Do not delete prior useful context
- Prefer updating over rewriting
- Keep entries short and high-signal

---

## Completion Checklist
- State file exists
- All sections updated
- Files modified are listed
- Next task is clearly defined