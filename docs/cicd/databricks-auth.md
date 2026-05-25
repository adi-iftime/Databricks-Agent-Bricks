# Databricks authentication in GitHub Actions

CI connects to the Databricks workspace using **repository secrets** — never commit credentials to the repo.

## Repository secrets

Configure these under **GitHub → Settings → Secrets and variables → Actions → Repository secrets**:

| Secret | Description |
|--------|-------------|
| `DATABRICKS_HOST` | Workspace URL (e.g. `https://adb-1234567890123456.7.azuredatabricks.net`) |
| `DATABRICKS_TOKEN` | Personal access token or service principal token with bundle validate permissions |

The [`databricks-cicd.yml`](../../.github/workflows/databricks-cicd.yml) workflow injects both as job-level environment variables for authenticated steps.

## Workflow usage

```yaml
env:
  DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
  DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}

steps:
  - uses: databricks/setup-cli@main
    with:
      version: 0.299.2
  - run: databricks current-user me
```

The **`databricks-auth`** job runs `databricks current-user me` on every PR/push to verify connectivity.

## Local development

Use CLI profiles in `~/.databrickscfg` (see [dab.md](../architecture/dab.md) target profiles). Do not copy production tokens into the repository.

### Terraform download / expired GPG key

If `databricks bundle validate` or `deploy` fails with:

```text
error downloading Terraform: unable to verify checksums signature: openpgp: key expired
```

upgrade the Databricks CLI to a patched release (for v0.299.x use **v0.299.2** or later). See [databricks/cli#5022](https://github.com/databricks/cli/issues/5022).

```bash
databricks --version   # e.g. v0.299.0 → needs patch
# Homebrew example:
brew upgrade databricks
# Or install script:
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh -s -- -v 0.299.2
```

CI pins `0.299.2` via `databricks/setup-cli` in workflow files.

## Permissions

Minimum for CI validate (SCRUM-122):

- Workspace access for bundle validate
- Unity Catalog read where bundle references catalogs (future deploy stories)

## Token rotation

1. Create a new token in Databricks (User Settings → Developer → Access tokens) or rotate SP secret.
2. Update `DATABRICKS_TOKEN` in GitHub repository secrets.
3. Run **Actions → Databricks CI/CD → Run workflow** (`workflow_dispatch`) and confirm `databricks-auth` passes.
4. Revoke the old token in Databricks.

## Staging / production

Use **GitHub Environments** with environment-scoped secrets when staging/prod deploy is enabled (Epic 2 follow-on). Dev CI uses repository-level secrets today.

## Related stories

- SCRUM-121 — auth wiring (this document)
- SCRUM-122 — `databricks bundle validate -t dev` gate
- SCRUM-120 — workflow scaffold
