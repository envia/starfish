# code2spec Claude Code install

- Slash-command skills: `.claude/skills/code2spec-*/SKILL.md`
- Support templates: `.claude/code2spec/templates/`
- Support rules: `.claude/code2spec/rules/`

Tool build metadata is recorded in `.code2spec-tools/build-info.json`.

Invoke from Claude Code by typing a slash command, e.g. `/code2spec-discovery`, `/code2spec-modules`, `/code2spec-finalize`, or `/code2spec-delta`.
After an initial full W1→W2→W3 run, `/code2spec-delta` is a single batch workflow; do not separately invoke modules/finalize for delta updates.
