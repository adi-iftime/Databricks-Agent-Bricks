-- Audit, lineage tags, and table metadata (SCRUM-134)
-- Catalog: mlops_intelligence_dev (dev target)
-- Apply after table DDL (01, 02) and optional grants (resources/grants/).

-- ---------------------------------------------------------------------------
-- UC tags for discovery, lineage, and agent tool filtering
-- ---------------------------------------------------------------------------

ALTER TABLE mlops_intelligence_dev.bronze_ops.pipeline_runs SET TAGS (
  'project' = 'mlops_intelligence',
  'domain' = 'pipeline',
  'layer' = 'bronze',
  'data_classification' = 'operational'
);

ALTER TABLE mlops_intelligence_dev.bronze_ops.system_metrics SET TAGS (
  'project' = 'mlops_intelligence',
  'domain' = 'infrastructure',
  'layer' = 'bronze',
  'data_classification' = 'operational'
);

ALTER TABLE mlops_intelligence_dev.bronze_ops.model_metrics SET TAGS (
  'project' = 'mlops_intelligence',
  'domain' = 'model',
  'layer' = 'bronze',
  'data_classification' = 'operational'
);

ALTER TABLE mlops_intelligence_dev.bronze_ops.feature_store_metrics SET TAGS (
  'project' = 'mlops_intelligence',
  'domain' = 'feature_store',
  'layer' = 'bronze',
  'data_classification' = 'operational'
);

-- ---------------------------------------------------------------------------
-- Schema-level tags (visible in UC explorer)
-- ---------------------------------------------------------------------------

ALTER SCHEMA mlops_intelligence_dev.bronze_ops SET TAGS (
  'project' = 'mlops_intelligence',
  'layer' = 'bronze'
);

ALTER SCHEMA mlops_intelligence_dev.silver_ops SET TAGS (
  'project' = 'mlops_intelligence',
  'layer' = 'silver'
);

ALTER SCHEMA mlops_intelligence_dev.gold_ops SET TAGS (
  'project' = 'mlops_intelligence',
  'layer' = 'gold'
);

-- ---------------------------------------------------------------------------
-- Audit log consumption stub — agent SP activity (query in SQL warehouse)
-- ---------------------------------------------------------------------------
-- Example: filter system.access.audit by service principal
-- SELECT event_time, user_identity.email, action_name, request_params
-- FROM system.access.audit
-- WHERE user_identity.email LIKE '%mlops-agent-sp%'
--   AND event_date >= current_date() - INTERVAL 7 DAYS
-- ORDER BY event_time DESC;
