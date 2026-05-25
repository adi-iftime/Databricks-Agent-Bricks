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

Stub jobs on the dev workspace use **serverless notebook tasks** (no `job_clusters`). `cluster_policy_id` applies when jobs use classic `new_cluster` blocks again.

When adding classic clusters, set the target variable and attach:

```yaml
policy_id: "${var.cluster_policy_id}"
```

Do not add `policy_id` while the variable default is empty — bundle validate fails on empty policy references.

## Serverless

Dev workspace requires serverless compute for job deploy. Stub jobs omit `job_clusters`; revisit policies when classic or governed serverless environments are introduced in Epic 7–9.

## Related

- SCRUM-129 — policy variable and job wiring
- [jobs.md](../architecture/jobs.md)
