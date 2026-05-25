# Cluster policies

ML Operations Intelligence jobs should run on clusters governed by Databricks **cluster policies** for cost and instance-type control.

## Bundle variable

| Variable | Purpose |
|----------|---------|
| `cluster_policy_id` | Policy ID applied to job `new_cluster` definitions |

Set per target in `databricks.yml` when a policy is provisioned in the workspace:

```yaml
targets:
  dev:
    variables:
      cluster_policy_id: "<dev-policy-id>"
```

Repository default is empty — jobs deploy without `policy_id` until your team sets the variable (no secrets in repo).

## Job attachment

After `cluster_policy_id` is set on a target, add to each job `new_cluster` block in `resources/jobs/*.job.yml`:

```yaml
policy_id: "${var.cluster_policy_id}"
```

Do not add `policy_id` while the variable default is empty — bundle validate fails on empty policy references.

## Serverless

Prefer serverless or policy-constrained single-node clusters for stub jobs; revisit sizing in Epic 7–9 implementation stories.

## Related

- SCRUM-129 — policy variable and job wiring
- [jobs.md](../architecture/jobs.md)
