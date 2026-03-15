-- =============================================================================
-- SEO Agent — Supabase Schema (MVP)
-- Apply via: supabase db push  OR  paste into SQL Editor in Supabase Dashboard
-- =============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── sites ──────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sites (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  domain text NOT NULL UNIQUE,
  name text,
  brand text,
  environment text DEFAULT 'production',
  freeze_until timestamptz NULL,
  created_at timestamptz DEFAULT now()
);

-- ─── head_terms ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS head_terms (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  term text NOT NULL,
  canonical_term text NOT NULL,
  created_at timestamptz DEFAULT now(),
  UNIQUE (canonical_term)
);

-- ─── owner_pages ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS owner_pages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id uuid REFERENCES sites(id) ON DELETE CASCADE,
  head_term_id uuid REFERENCES head_terms(id) ON DELETE CASCADE,
  path text NOT NULL,
  title text,
  h1 text,
  canonical text,
  json_rules jsonb DEFAULT '{}',
  json_ld jsonb,
  last_deployed_at timestamptz,
  UNIQUE (site_id, head_term_id)
);

-- ─── internal_links ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS internal_links (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id uuid REFERENCES sites(id),
  source_path text NOT NULL,
  target_owner_page_id uuid REFERENCES owner_pages(id),
  anchor text,
  created_at timestamptz DEFAULT now()
);

-- ─── pr_queue ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pr_queue (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id uuid REFERENCES sites(id),
  owner_page_id uuid REFERENCES owner_pages(id),
  pr_url text,
  branch_name text,
  status text DEFAULT 'open' CHECK (status IN ('open', 'approved', 'merged', 'rejected', 'reverted')),
  diff jsonb,
  created_by text DEFAULT 'seo-agent',
  created_at timestamptz DEFAULT now(),
  processed_at timestamptz
);

-- ─── audit_logs ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  actor text DEFAULT 'seo-agent',
  action text NOT NULL,
  payload jsonb DEFAULT '{}',
  created_at timestamptz DEFAULT now()
);

-- ─── index_requests ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS index_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id uuid REFERENCES sites(id),
  path text NOT NULL,
  request_status text DEFAULT 'pending' CHECK (request_status IN ('pending', 'submitted', 'confirmed', 'failed')),
  response jsonb,
  requested_at timestamptz DEFAULT now(),
  processed_at timestamptz
);

-- ─── monitor_metrics ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS monitor_metrics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id uuid REFERENCES sites(id),
  owner_page_id uuid REFERENCES owner_pages(id),
  metric_date date NOT NULL,
  impressions bigint DEFAULT 0,
  clicks bigint DEFAULT 0,
  ctr numeric DEFAULT 0,
  avg_position numeric DEFAULT 0,
  owner_share numeric DEFAULT 0,
  homepage_impressions bigint DEFAULT 0,
  raw_gsc jsonb,
  created_at timestamptz DEFAULT now(),
  UNIQUE(site_id, owner_page_id, metric_date)
);

-- ─── Indexes ────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_owner_pages_site ON owner_pages(site_id);
CREATE INDEX IF NOT EXISTS idx_owner_pages_term ON owner_pages(head_term_id);
CREATE INDEX IF NOT EXISTS idx_monitor_date ON monitor_metrics(metric_date);
CREATE INDEX IF NOT EXISTS idx_pr_queue_status ON pr_queue(status);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_index_requests_status ON index_requests(request_status);

-- ─── Seed data (SP / AN / WP) ──────────────────────────────────────────────
INSERT INTO sites (domain, name, brand, environment, freeze_until) VALUES
  ('superparty.ro', 'SuperParty', 'SuperParty', 'production', '2026-03-21T23:59:59Z'),
  ('animatopia.ro', 'Animatopia', 'Animatopia', 'production', NULL),
  ('wowparty.ro', 'WowParty', 'WowParty', 'production', NULL)
ON CONFLICT (domain) DO NOTHING;

INSERT INTO head_terms (term, canonical_term) VALUES
  ('animatori petreceri copii', 'animatori petreceri copii'),
  ('mascote si personaje', 'mascote si personaje'),
  ('petreceri tematice', 'petreceri tematice'),
  ('petreceri acasa', 'petreceri acasa'),
  ('pachete animatori', 'pachete animatori')
ON CONFLICT (canonical_term) DO NOTHING;
