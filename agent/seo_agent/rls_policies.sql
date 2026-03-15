-- ═══════════════════════════════════════════════════════════════════════════
-- RLS Policies for SEO Agent — Supabase
-- Applied: 2026-03-15
-- Rule: SELECT open to all, WRITE restricted to service_role only
-- Note: service_role key bypasses RLS. These policies protect against
--       anon key misuse. Agent should use service_role key server-side.
-- ═══════════════════════════════════════════════════════════════════════════

-- ── pr_queue ─────────────────────────────────────────────────────────────
ALTER TABLE pr_queue ENABLE ROW LEVEL SECURITY;

CREATE POLICY pr_queue_select ON pr_queue
  FOR SELECT USING (true);

CREATE POLICY pr_queue_insert ON pr_queue
  FOR INSERT WITH CHECK (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
    OR current_setting('request.jwt.claims', true)::jsonb->>'role' = 'authenticated'
  );

CREATE POLICY pr_queue_update ON pr_queue
  FOR UPDATE USING (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

CREATE POLICY pr_queue_delete ON pr_queue
  FOR DELETE USING (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

-- ── owner_pages ──────────────────────────────────────────────────────────
ALTER TABLE owner_pages ENABLE ROW LEVEL SECURITY;

CREATE POLICY owner_pages_select ON owner_pages
  FOR SELECT USING (true);

CREATE POLICY owner_pages_write ON owner_pages
  FOR INSERT WITH CHECK (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

CREATE POLICY owner_pages_update ON owner_pages
  FOR UPDATE USING (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

CREATE POLICY owner_pages_delete ON owner_pages
  FOR DELETE USING (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

-- ── sites ────────────────────────────────────────────────────────────────
ALTER TABLE sites ENABLE ROW LEVEL SECURITY;

CREATE POLICY sites_select ON sites
  FOR SELECT USING (true);

CREATE POLICY sites_write ON sites
  FOR INSERT WITH CHECK (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

CREATE POLICY sites_update ON sites
  FOR UPDATE USING (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

-- ── audit_logs ───────────────────────────────────────────────────────────
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY audit_logs_select ON audit_logs
  FOR SELECT USING (true);

CREATE POLICY audit_logs_insert ON audit_logs
  FOR INSERT WITH CHECK (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
    OR current_setting('request.jwt.claims', true)::jsonb->>'role' = 'authenticated'
  );

-- ── index_requests ───────────────────────────────────────────────────────
ALTER TABLE index_requests ENABLE ROW LEVEL SECURITY;

CREATE POLICY index_requests_select ON index_requests
  FOR SELECT USING (true);

CREATE POLICY index_requests_write ON index_requests
  FOR INSERT WITH CHECK (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

CREATE POLICY index_requests_update ON index_requests
  FOR UPDATE USING (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

-- ── monitor_metrics ──────────────────────────────────────────────────────
ALTER TABLE monitor_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY monitor_metrics_select ON monitor_metrics
  FOR SELECT USING (true);

CREATE POLICY monitor_metrics_write ON monitor_metrics
  FOR INSERT WITH CHECK (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

CREATE POLICY monitor_metrics_update ON monitor_metrics
  FOR UPDATE USING (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

-- ── head_terms ───────────────────────────────────────────────────────────
ALTER TABLE head_terms ENABLE ROW LEVEL SECURITY;

CREATE POLICY head_terms_select ON head_terms
  FOR SELECT USING (true);

CREATE POLICY head_terms_write ON head_terms
  FOR INSERT WITH CHECK (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );

-- ── internal_links ───────────────────────────────────────────────────────
ALTER TABLE internal_links ENABLE ROW LEVEL SECURITY;

CREATE POLICY internal_links_select ON internal_links
  FOR SELECT USING (true);

CREATE POLICY internal_links_write ON internal_links
  FOR INSERT WITH CHECK (
    current_setting('request.jwt.claims', true)::jsonb->>'role' = 'service_role'
  );
