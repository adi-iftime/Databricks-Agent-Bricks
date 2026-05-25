-- Unity Catalog RBAC for ML Operations Intelligence (SCRUM-133)
-- Catalog: mlops_intelligence_dev (dev target)
--
-- Prerequisites:
--   1. Catalog and tables created (resources/sql/00_catalog.sql … 02_ml_metrics_tables.sql)
--   2. Service principals exist in the workspace:
--        mlops-ingestion-sp — pipeline writers (Jobs API → bronze/silver)
--        mlops-agent-sp     — read-only agent queries (gold_ops)
--
-- Apply order: after DDL, before ingestion jobs run.
-- Replace backtick principals if your workspace uses application IDs instead of display names.

-- ---------------------------------------------------------------------------
-- Ingestion service principal — write bronze/silver only
-- ---------------------------------------------------------------------------
GRANT USE CATALOG ON CATALOG mlops_intelligence_dev TO `mlops-ingestion-sp`;
GRANT USE SCHEMA ON SCHEMA mlops_intelligence_dev.bronze_ops TO `mlops-ingestion-sp`;
GRANT USE SCHEMA ON SCHEMA mlops_intelligence_dev.silver_ops TO `mlops-ingestion-sp`;

GRANT MODIFY ON SCHEMA mlops_intelligence_dev.bronze_ops TO `mlops-ingestion-sp`;
GRANT MODIFY ON SCHEMA mlops_intelligence_dev.silver_ops TO `mlops-ingestion-sp`;

GRANT MODIFY ON TABLE mlops_intelligence_dev.bronze_ops.pipeline_runs TO `mlops-ingestion-sp`;
GRANT MODIFY ON TABLE mlops_intelligence_dev.bronze_ops.system_metrics TO `mlops-ingestion-sp`;
GRANT MODIFY ON TABLE mlops_intelligence_dev.bronze_ops.model_metrics TO `mlops-ingestion-sp`;
GRANT MODIFY ON TABLE mlops_intelligence_dev.bronze_ops.feature_store_metrics TO `mlops-ingestion-sp`;

-- Explicitly withhold gold read/write from ingestion (documented negative expectation).
-- No GRANT on gold_ops for mlops-ingestion-sp.

-- ---------------------------------------------------------------------------
-- Agent service principal — read gold_ops only
-- ---------------------------------------------------------------------------
GRANT USE CATALOG ON CATALOG mlops_intelligence_dev TO `mlops-agent-sp`;
GRANT USE SCHEMA ON SCHEMA mlops_intelligence_dev.gold_ops TO `mlops-agent-sp`;
GRANT SELECT ON SCHEMA mlops_intelligence_dev.gold_ops TO `mlops-agent-sp`;

-- Agent must NOT receive MODIFY on bronze/silver (negative test: INSERT pipeline_runs fails).
-- No GRANT MODIFY on bronze_ops or silver_ops for mlops-agent-sp.

-- ---------------------------------------------------------------------------
-- CI deploy principal (optional — set principal name in workspace)
-- ---------------------------------------------------------------------------
-- GRANT USE CATALOG ON CATALOG mlops_intelligence_dev TO `mlops-cicd-sp`;
-- GRANT CREATE SCHEMA ON CATALOG mlops_intelligence_dev TO `mlops-cicd-sp`;
-- GRANT ALL PRIVILEGES ON SCHEMA mlops_intelligence_dev.bronze_ops TO `mlops-cicd-sp`;
