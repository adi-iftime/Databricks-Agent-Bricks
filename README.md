# Databricks Agent Bricks — ML Operations Intelligence

Enterprise **ML-aware operational intelligence** on Databricks: governed data in Unity Catalog, anomaly detection, and an Agent Bricks–style ML Ops agent with full **GitHub → CI/CD → DAB** deployment.

This repository is also a **Cursor AI SDLC framework** (`.cursor/` agents, rules, skills, hooks). Platform code lives alongside that framework without replacing it.

## Repository layout

```text
Databricks-Agent-Bricks/
├── .cursor/                 # Cursor orchestration (framework)
├── src/mlops_intelligence/  # Python platform package
├── notebooks/               # Deployable Databricks notebooks
├── resources/               # DAB jobs, SQL, grants
├── tests/                   # Unit tests
├── docs/                    # Architecture & runbooks
├── databricks.yml           # Asset Bundle manifest
└── .github/workflows/       # CI/CD
```

See [docs/architecture/repo-layout.md](docs/architecture/repo-layout.md) for boundaries between framework and application code.

## Evolution

| Phase | What |
|-------|------|
| **Today** | Cursor template + Wave 1 scaffold (SCRUM-115) |
| **Next** | DAB targets, GHA deploy, UC tables, ingestion, agent (Jira SCRUM-103–114) |

## Local verification

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

Optional: `pip install -e ".[dev]"` and `ruff check .cursor/hooks` (see [CONTRIBUTING.md](CONTRIBUTING.md)).

## Contributing

One Jira story per PR, Jira key in title, tests required. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Jira

Backlog: project **SCRUM**, labels `mlops-intelligence`, `databricks`, `agent-bricks`.
