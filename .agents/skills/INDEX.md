# Codex Skills Index

Codex-native skills live under `.agents/skills/`. These skills complement, but do not fully
replace, legacy Claude Code skills under `.claude/skills/`.

| Skill | Path | Use when | Key artifacts |
|---|---|---|---|
| `independent-review` | `.agents/skills/independent-review/SKILL.md` | The user wants a provider-neutral blind second-pass validation, second opinion, cross-check, or independent re-derivation. | `working/independent_review/`, `.knowledge/independent-review/log.jsonl` |
| `claude-review` | `.agents/skills/claude-review/SKILL.md` | Codex produced an analysis and the user wants Claude to independently validate it from a blind brief. | `working/claude_review/`, `.knowledge/claude-review/log.jsonl` |
| `skill-parity-review` | `.agents/skills/skill-parity-review/SKILL.md` | The user wants to compare a Codex skill with its corresponding Claude skill, audit migration parity, port a Claude skill to Codex, or bring a Codex skill up to parity. | `working/skill_parity_review/` |

## Legacy Claude compatibility

- Legacy Claude skills remain under `.claude/skills/`.
- Legacy Claude `/codex-review` remains at `.claude/skills/codex-review/SKILL.md`.
- Codex users should prefer `$independent-review` for provider-neutral validation and
  `$claude-review` when Claude should validate a Codex result.
