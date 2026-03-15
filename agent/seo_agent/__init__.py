"""
seo_agent — Autonomous SEO Agent for multi-brand anti-cannibalization.

Components:
  - rules_engine: Policy enforcement (freeze, owner uniqueness, canary)
  - owner_mapper: Head-term → owner page mapping
  - supabase_client: Database CRUD wrapper
  - template_engine: JSON-LD / meta template generation
  - pr_generator: Branch + PR creation with HITL checklist
  - index_notify: GSC Indexing API + sitemap submit
  - monitor: GSC/GA4 metric collection + owner_share calculation
  - alerting: Threshold-based alert dispatcher
  - canary_orchestrator: Canary → wave rollout coordination
  - rollback: Automated revert + CDN purge + reindex
"""

__version__ = "0.1.0"
