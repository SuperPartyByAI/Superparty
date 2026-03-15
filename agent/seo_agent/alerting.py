"""
alerting.py — Slack/webhook alert integration.

Sends alerts when monitor thresholds are violated.
Configurable via env vars or direct parameters.
"""
from __future__ import annotations

import json
import logging
import os
import urllib.request
import urllib.error
from typing import Optional

log = logging.getLogger("seo_agent.alerting")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


def send_slack_alert(
    report: dict,
    webhook_url: Optional[str] = None,
) -> tuple[bool, str]:
    """
    Send alert to Slack via Incoming Webhook.
    
    report: output from generate_daily_report() or daily_report.generate_report()
    webhook_url: Slack webhook URL (falls back to SLACK_WEBHOOK_URL env var)
    """
    url = webhook_url or SLACK_WEBHOOK_URL
    if not url:
        log.warning("No Slack webhook URL configured — alert not sent")
        return False, "No webhook URL"

    severity = report.get("verdict", "unknown")
    emoji = "🔴" if severity == "critical" else "🟡" if severity == "warning" else "🟢"

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"{emoji} SEO Alert — {report.get('site', 'unknown')}",
            }
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Head Term:*\n{report.get('head_term', '—')}"},
                {"type": "mrkdwn", "text": f"*Severity:*\n{severity.upper()}"},
                {"type": "mrkdwn", "text": f"*Owner Share:*\n{report.get('owner_share', 0):.1f}%"},
                {"type": "mrkdwn", "text": f"*Date:*\n{report.get('date', '—')}"},
                {"type": "mrkdwn", "text": f"*Owner Clicks:*\n{report.get('owner_clicks', 0)}"},
                {"type": "mrkdwn", "text": f"*Owner CTR:*\n{report.get('owner_ctr', 0):.2f}%"},
            ],
        },
    ]

    # Add alerts section
    alerts = report.get("alerts", [])
    if alerts:
        alert_text = "\n".join(f"• {a}" for a in alerts)
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Alerts:*\n{alert_text}"},
        })

    # Add trend if available
    trend = report.get("trend")
    if trend:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"*Trend vs Baseline:*\n"
                    f"owner_share: {trend.get('owner_share_delta', 0):+.1f}pp {trend.get('direction', '→')}\n"
                    f"impressions: {trend.get('impr_delta', 0):+d} | "
                    f"clicks: {trend.get('clicks_delta', 0):+d}"
                ),
            },
        })

    payload = {"blocks": blocks}

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                log.info("Slack alert sent successfully")
                return True, "sent"
            else:
                msg = f"Slack returned status {resp.status}"
                log.error(msg)
                return False, msg

    except urllib.error.URLError as e:
        msg = f"Slack webhook error: {e}"
        log.error(msg)
        return False, msg
    except Exception as e:
        msg = f"Unexpected error: {e}"
        log.error(msg)
        return False, msg


def send_simple_message(
    text: str,
    webhook_url: Optional[str] = None,
) -> tuple[bool, str]:
    """Send a simple text message to Slack."""
    url = webhook_url or SLACK_WEBHOOK_URL
    if not url:
        return False, "No webhook URL"

    payload = {"text": text}
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200, f"status={resp.status}"
    except Exception as e:
        return False, str(e)


def format_report_text(report: dict) -> str:
    """Format report as plain text for email/log."""
    lines = [
        f"SEO Report — Day {report.get('day', '?')} — {report.get('site', '?')}",
        f"Date: {report.get('date', '?')}",
        f"Query: {report.get('head_term', '?')}",
        f"",
        f"owner_share: {report.get('owner_share', 0):.1f}%",
        f"owner impressions: {report.get('owner_impressions', 0)}",
        f"homepage impressions: {report.get('homepage_impressions', 0)}",
        f"owner clicks: {report.get('owner_clicks', 0)}",
        f"owner CTR: {report.get('owner_ctr', 0):.2f}%",
        f"owner position: {report.get('owner_position', 0):.1f}",
        f"",
        f"Verdict: {report.get('verdict', '?').upper()}",
    ]
    for a in report.get("alerts", []):
        lines.append(f"  ⚠ {a}")
    return "\n".join(lines)
