# Orchestration artifacts (optional)

Optional files for **manual** multi-agent discipline. They are **not** read by the default [`.cursor/hooks.json`](../hooks.json) (only advisory `postToolUse` hooks are registered).

- **`last_story.json`** — Optional checklist for workers: `acceptance_criteria` (string), `worker_agent` (string), `dependencies` (list or string). See [last_story.example.json](last_story.example.json).

- **`locks.json`** — Optional path locks for pipeline areas. **Gitignored** locally if used. Schema: [locks.schema.json](locks.schema.json).

## Task tool: planning vs implementation (policy reference)

[`../hooks/policies/orchestration_agents.json`](../hooks/policies/orchestration_agents.json) documents recommended **planning** vs **implementation** `subagent_type` conventions for teams using the Task tool. Nothing in the current hook set enforces Jira keys or `OWNERSHIP=` at the editor.

**Jira:** Use the **Atlassian MCP** per [`.cursor/rules/jira-atlassian-mcp.mdc`](../rules/jira-atlassian-mcp.mdc).
