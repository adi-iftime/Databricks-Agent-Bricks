---
name: pipeline-testing
description: Designs pipeline tests around architecture, schemas, transforms, incremental and idempotent behavior, streaming recovery, partitioning, performance risk, and observability checkpoints; favors deterministic reusable tests. Use when modifying ETL or ELT pipelines, implementing PySpark transformations, modifying streaming jobs, implementing Delta Lake logic, validating medallion architecture layers, testing Dagster or orchestration workflows, validating schema evolution, or testing distributed data processing systems.
---

# Pipeline Testing

Load this skill when:

- modifying ETL or ELT pipelines
- implementing PySpark transformations
- modifying streaming jobs
- implementing Delta Lake logic
- validating medallion architecture layers
- testing Dagster or orchestration workflows
- validating schema evolution
- testing distributed data processing systems

## Workflow

1. Analyze the pipeline architecture, transformations, inputs, and outputs.
2. Validate schema consistency and schema evolution handling.
3. Generate tests for null handling, edge cases, and invalid inputs.
4. Validate transformation correctness and business logic consistency.
5. Test incremental processing and idempotency behavior.
6. Validate streaming checkpointing, retries, and recovery behavior when applicable.
7. Validate partitioning strategies and data distribution assumptions.
8. Detect performance risks and scalability bottlenecks.
9. Ensure observability through logging, metrics, and validation checkpoints.
10. Produce deterministic, maintainable, and reusable pipeline tests.

Pipeline Testing Rules:
- Validate schema consistency.
- Validate null handling and edge cases.
- Validate incremental processing behavior.
- Validate idempotency whenever applicable.
- Add observability validation for production pipelines.
- Test failure and retry scenarios for streaming pipelines.

Required Validation Areas:

Schema Validation
Null Handling
Transformation Correctness
Incremental Processing
Idempotency
Retry and Recovery Logic
Partitioning Strategy
Performance Risks

## Notes (non-normative)

- Prefer small representative datasets and fixed seeds; isolate external systems with fakes or recorded inputs when the orchestrator allows.
- Map each test plan or suite explicitly to the **Required Validation Areas** so coverage gaps are visible before merge.
