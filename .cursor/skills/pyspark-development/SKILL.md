---
name: pyspark-development
description: >-
  Guides PySpark and Spark pipeline work: align with existing architecture and
  patterns, scalable distributed transforms, join/shuffle/partition/memory
  tuning, robust schema and null handling, observability, tests, modular reuse,
  and Delta Lake or medallion compatibility when relevant. Use when modifying
  PySpark pipelines, implementing ETL or ELT, processing distributed datasets,
  working with Delta Lake, implementing streaming pipelines, optimizing Spark
  jobs, working in Databricks environments, or implementing medallion
  architecture layers.
---

# PySpark Development

Load this skill when:

- modifying PySpark pipelines
- implementing ETL or ELT workflows
- processing distributed datasets
- working with Delta Lake
- implementing streaming pipelines
- optimizing Spark jobs
- working in Databricks environments
- implementing medallion architecture layers

## Workflow

1. Analyze the existing Spark or PySpark pipeline architecture.
2. Follow existing project structure, naming conventions, and transformation patterns.
3. Implement scalable distributed data processing logic.
4. Optimize joins, partitioning, shuffles, caching, and memory usage.
5. Ensure schema handling and null handling are robust.
6. Implement observability through logging and metrics.
7. Add unit tests and validation checks for transformations.
8. Prefer reusable transformations and modular pipeline design.
9. Avoid driver-side bottlenecks and unnecessary data collection.
10. Ensure compatibility with Delta Lake and medallion architecture patterns when applicable.

PySpark Development Rules:
- Avoid unnecessary shuffles.
- Avoid collect() on large datasets.
- Prefer explicit schemas.
- Prefer incremental transformations.
- Add logging and metrics for production pipelines.
- Validate schema evolution compatibility.
- Add tests for edge cases and null handling.

Required Validation Areas:

Schema Validation
Null Handling
Partitioning Strategy
Performance Risks
Distributed Processing Safety

## Implementation notes (non-normative)

- Before changing joins: check join key nullability, skew, and broadcast thresholds; prefer partition pruning and predicate pushdown where the catalog supports it.
- For Delta: use merge semantics, constraints, and expectations where they match project standards; document `mergeSchema` / evolution decisions in code or ticket text.
- For tests: use local or small-fixture Spark sessions; assert output schemas and row counts on representative partitions, not only happy paths.
