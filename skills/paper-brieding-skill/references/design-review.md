# Paper Brieding Skill Design Review

This note records the first-pass review that motivated the suite structure.

## Sources Reviewed

- Academic Research Skills Codex:
  https://github.com/Imbad0202/academic-research-skills-codex
- Nature Skills:
  https://github.com/Yuan1z0825/nature-skills
- Nature Reader:
  https://github.com/Yuan1z0825/nature-skills/blob/main/skills/nature-reader/SKILL.md
- Nature Paper2PPT:
  https://github.com/Yuan1z0825/nature-skills/blob/main/skills/nature-paper2ppt/SKILL.md
- Nature Reviewer:
  https://github.com/Yuan1z0825/nature-skills/blob/main/skills/nature-reviewer/SKILL.md
- Writing Great Skills:
  https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-great-skills/SKILL.md

## Borrowed Ideas

- Use a router instead of one large skill.
- Load only the workflow needed for the current task.
- Make outputs source-grounded and mark uncertainty.
- Treat report writing and oral teaching as different products.
- Add reviewer-style critique as a first-class workflow.
- Keep SKILL.md concise and push background notes into references.

## Avoided Ideas

- Full research pipeline scope by default.
- Mandatory full-paper translation for every read.
- Nature-specific deck assumptions as the default report format.
- Large static doctrine files that load for every request.

## Suite Shape

- `paper-brieding-skill`: entrypoint and task routing.
- `paper-reader`: source-grounded understanding.
- `paper-report`: durable written report.
- `paper-teacher`: oral explanation and Q&A prep.
- `paper-reviewer`: critique and reproduction risk.
- `paper-writing`: related writing and prose support.
