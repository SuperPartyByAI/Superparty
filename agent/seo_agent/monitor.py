"""
monitor.py — GSC/GA4 metric collection + owner_share calculation.

Fetches performance data, computes owner_share, detects threshold
violations, and triggers alerts.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

log = logging.getLogger("seo_agent.monitor")


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class PageMetrics:
    """Metrics for a single page for a query."""
    url: str
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    avg_position: float = 0.0


@dataclass
class OwnerShareResult:
    """Result of owner_share calculation."""
    owner_impressions: int = 0
    homepage_impressions: int = 0
    total_impressions: int = 0
    owner_share: float = 0.0
    owner_clicks: int = 0
    homepage_clicks: int = 0
    owner_ctr: float = 0.0
    homepage_ctr: float = 0.0
    owner_position: float = 0.0
    homepage_position: float = 0.0


@dataclass
class AlertThresholds:
    """Configurable alert thresholds."""
    min_owner_share: float = 0.30  # 30% — alert if below
    target_owner_share: float = 0.60  # 60% — merge target
    max_ctr_regression: float = 0.15  # 15% — alert if CTR drops more
    max_clicks_regression: float = 0.15  # 15% — alert if clicks drop more


@dataclass
class AlertResult:
    """Result of threshold check."""
    has_alerts: bool = False
    alerts: list[str] = field(default_factory=list)
    severity: str = "ok"  # ok, warning, critical

    def add_alert(self, msg: str, level: str = "warning"):
        self.has_alerts = True
        self.alerts.append(msg)
        if level == "critical" or self.severity == "critical":
            self.severity = "critical"
        elif level == "warning" and self.severity != "critical":
            self.severity = "warning"


# ── Calculations ─────────────────────────────────────────────────────────────

def calculate_owner_share(
    page_metrics: list[PageMetrics],
    owner_path: str,
    homepage_path: str = "/",
) -> OwnerShareResult:
    """
    Calculate owner_share from per-page metrics.
    
    owner_share = owner_impressions / (owner_impressions + homepage_impressions) * 100
    """
    result = OwnerShareResult()

    for pm in page_metrics:
        # Normalize URL to path
        path = pm.url
        if "://" in path:
            path = "/" + "/".join(path.split("/")[3:])
        path = path.rstrip("/") or "/"

        owner_normalized = owner_path.rstrip("/") or "/"
        homepage_normalized = homepage_path.rstrip("/") or "/"

        if path == owner_normalized:
            result.owner_impressions = pm.impressions
            result.owner_clicks = pm.clicks
            result.owner_ctr = pm.ctr
            result.owner_position = pm.avg_position
        elif path == homepage_normalized:
            result.homepage_impressions = pm.impressions
            result.homepage_clicks = pm.clicks
            result.homepage_ctr = pm.ctr
            result.homepage_position = pm.avg_position

    result.total_impressions = result.owner_impressions + result.homepage_impressions

    if result.total_impressions > 0:
        result.owner_share = result.owner_impressions / result.total_impressions
    else:
        result.owner_share = 0.0

    return result


def check_thresholds(
    current: OwnerShareResult,
    baseline: Optional[OwnerShareResult] = None,
    thresholds: Optional[AlertThresholds] = None,
) -> AlertResult:
    """
    Check current metrics against thresholds and baseline.
    Returns alert results.
    """
    t = thresholds or AlertThresholds()
    alert = AlertResult()

    # 1. Owner share too low
    if current.owner_share < t.min_owner_share:
        alert.add_alert(
            f"CRITICAL: owner_share = {current.owner_share:.1%} "
            f"(below {t.min_owner_share:.0%} threshold)",
            level="critical",
        )

    # 2. Owner share not at target (warning only)
    elif current.owner_share < t.target_owner_share:
        alert.add_alert(
            f"WARNING: owner_share = {current.owner_share:.1%} "
            f"(below {t.target_owner_share:.0%} target)",
            level="warning",
        )

    # 3. CTR regression vs baseline
    if baseline and baseline.owner_ctr > 0:
        ctr_change = (current.owner_ctr - baseline.owner_ctr) / baseline.owner_ctr
        if ctr_change < -t.max_ctr_regression:
            alert.add_alert(
                f"CRITICAL: CTR dropped {abs(ctr_change):.1%} "
                f"(baseline {baseline.owner_ctr:.2%} → current {current.owner_ctr:.2%})",
                level="critical",
            )

    # 4. Clicks regression vs baseline
    if baseline and baseline.owner_clicks > 0:
        clicks_change = (current.owner_clicks - baseline.owner_clicks) / baseline.owner_clicks
        if clicks_change < -t.max_clicks_regression:
            alert.add_alert(
                f"WARNING: Clicks dropped {abs(clicks_change):.1%} "
                f"(baseline {baseline.owner_clicks} → current {current.owner_clicks})",
                level="warning",
            )

    # 5. Owner position worse than homepage (warning)
    if current.owner_position > 0 and current.homepage_position > 0:
        if current.owner_position > current.homepage_position + 2:
            alert.add_alert(
                f"WARNING: Owner avg position ({current.owner_position:.1f}) "
                f"worse than homepage ({current.homepage_position:.1f})",
                level="warning",
            )

    return alert


def parse_gsc_response(gsc_rows: list[dict], query: str) -> list[PageMetrics]:
    """
    Parse GSC API response rows into PageMetrics.
    Expects rows from searchanalytics().query() with page dimension.
    """
    metrics = []
    for row in gsc_rows:
        keys = row.get("keys", [])
        if not keys:
            continue
        # With page dimension, first key is the page URL
        url = keys[0] if len(keys) == 1 else keys[-1]
        metrics.append(PageMetrics(
            url=url,
            impressions=int(row.get("impressions", 0)),
            clicks=int(row.get("clicks", 0)),
            ctr=float(row.get("ctr", 0)),
            avg_position=float(row.get("position", 0)),
        ))
    return metrics


def generate_daily_report(
    site_domain: str,
    head_term: str,
    share_result: OwnerShareResult,
    alert_result: AlertResult,
    metric_date: Optional[date] = None,
) -> dict:
    """
    Generate a structured daily monitoring report.
    """
    d = metric_date or date.today()

    return {
        "date": d.isoformat(),
        "site": site_domain,
        "head_term": head_term,
        "owner_share": round(share_result.owner_share * 100, 1),
        "owner_impressions": share_result.owner_impressions,
        "homepage_impressions": share_result.homepage_impressions,
        "owner_clicks": share_result.owner_clicks,
        "homepage_clicks": share_result.homepage_clicks,
        "owner_ctr": round(share_result.owner_ctr * 100, 2),
        "homepage_ctr": round(share_result.homepage_ctr * 100, 2),
        "owner_position": round(share_result.owner_position, 1),
        "homepage_position": round(share_result.homepage_position, 1),
        "verdict": alert_result.severity,
        "alerts": alert_result.alerts,
    }
