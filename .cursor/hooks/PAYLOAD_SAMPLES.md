# Cursor hook stdin reference

Cursor sends JSON on stdin. Prefer **`tool_name`** and **`tool_input`** (see [Hooks docs](https://cursor.com/docs/hooks)).

## Active hooks (this repo)

[`.cursor/hooks.json`](../hooks.json) uses **only** `postToolUse` hooks with `failClosed: false` — they add **additional_context** hints and **do not** deny tools.

| Script | Matcher | Purpose |
|--------|---------|---------|
| `de_spark_quality_static.py` | `Write`, `StrReplace` | PySpark / pipeline suggestions from [policies/spark_rules.json](policies/spark_rules.json) (reads file from disk after write). |
| `de_pr_quality_inject.py` | `Shell` | PR checklist text when using `gh pr create` / `edit`. |
| `de_pipeline_tests_coach.py` | `Write`, `StrReplace` | Testing / schema suggestions when pipeline paths change. |

## `subagentStop`

Not registered. Optional Jira gate scripts under `.cursor/hooks/` are **not** wired unless you add them to `hooks.json`.

## Task / orchestration

No hook enforces Jira keys or `OWNERSHIP=` on `Task`. See `policies/orchestration_agents.json` for **documentation-only** planning vs implementation conventions.
