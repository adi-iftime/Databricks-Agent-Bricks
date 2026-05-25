-- Unity Catalog foundation for ML Operations Intelligence (SCRUM-130)
-- Apply per DAB target; catalog name must match databricks.yml variable `catalog`.
-- Dev: mlops_intelligence_dev | Staging: mlops_intelligence_staging | Prod: mlops_intelligence_prod

-- Example for dev target (replace catalog prefix when running against staging/prod):
CREATE CATALOG IF NOT EXISTS mlops_intelligence_dev
  COMMENT 'ML Operations Intelligence — development';

CREATE SCHEMA IF NOT EXISTS mlops_intelligence_dev.bronze_ops
  COMMENT 'Bronze operational signals (raw/near-raw)';

CREATE SCHEMA IF NOT EXISTS mlops_intelligence_dev.silver_ops
  COMMENT 'Silver curated operational metrics';

CREATE SCHEMA IF NOT EXISTS mlops_intelligence_dev.gold_ops
  COMMENT 'Gold aggregates for agent and dashboards';

-- Restrict default access; grant via dedicated security stories (Epic 10).
-- REVOKE is environment-specific — apply in workspace after catalog creation.
