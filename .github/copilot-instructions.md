# GitHub Copilot Instructions

This repository uses GitHub Copilot with a lightweight, explicit instruction structure.

## Source of guidance
- Treat this file as the primary repository instruction file.
- Reusable guidance lives in `.github/skills/`.
- Task-specific prompts live in `.github/prompts/`.
- Project planning and state artifacts, if needed, live in `.github/repo/`.

## Working approach
- Prefer small, reviewable changes.
- Preserve existing behavior unless the task explicitly requires changing it.
- Read relevant repository guidance before making edits.
- Keep plans, assumptions, and open questions explicit in commit-ready work products.
- Avoid inventing files, tools, frameworks, or workflows unless the task clearly calls for them.

## Skill loading
Before substantial work, review the applicable files in `.github/skills/`.
At minimum, consider:
- `compliance_guard.md`
- `minimal_change_discipline.md`
- `state_tracking.md`
- `style_guide.md`

## State and planning
- Use `.github/repo/project_state.md` when active work requires explicit state tracking.
- Record major architectural or workflow decisions in `.github/repo/decisions.md` when such files are being used.
- Do not assume any specific application structure unless it already exists in the repository or is requested in the task.
