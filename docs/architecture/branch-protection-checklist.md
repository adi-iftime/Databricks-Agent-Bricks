# Branch protection checklist

Use when configuring GitHub **Branch protection rules** for ML Operations Intelligence. Settings are applied in the GitHub UI (not in-repo).

## `main`

- [ ] Require a pull request before merging
- [ ] Require approvals: **1**
- [ ] Dismiss stale pull request approvals when new commits are pushed
- [ ] Require status checks to pass: `hooks-and-policies`
- [ ] Require branches to be up to date before merging
- [ ] Restrict pushes that create files (optional)
- [ ] Do not allow bypassing the above settings
- [ ] Restrict who can push to matching branches (maintainers only)
- [ ] Block force pushes
- [ ] Block deletions

## `dev`

- [ ] Require a pull request before merging
- [ ] Require status checks to pass: `hooks-and-policies`
- [ ] Require branches to be up to date before merging
- [ ] Restrict who can push to matching branches
- [ ] Block force pushes
- [ ] Block deletions

## Verification

```bash
# Confirm dev exists
git ls-remote --heads origin dev

# Smoke: open a draft PR from feature/* → dev and confirm required checks appear
gh pr create --base dev --head feature/SCRUM-XXX-test --draft
```

Record completion date and admin who applied rules in your team runbook.
