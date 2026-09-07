# code2spec Gemini CLI install

- Project skills: `.gemini/skills/code2spec-*/SKILL.md`
- Project commands: `.gemini/commands/code2spec-*.toml`
- Support templates: `.gemini/code2spec/templates/`
- Support rules: `.gemini/code2spec/rules/`

Tool build metadata is recorded in `.code2spec-tools/build-info.json`.

Invoke from Gemini CLI with slash commands, e.g. `/code2spec-discovery`, `/code2spec-modules`, `/code2spec-finalize`, or `/code2spec-delta`.
After an initial full W1→W2→W3 run, `/code2spec-delta` is a single batch workflow; do not separately invoke modules/finalize for delta updates.
