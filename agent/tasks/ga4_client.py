"""ga4_client.py — GA4 Data API client using service account credentials."""
import json, os
from datetime import date, timedelta

def _get_creds(scopes=None):
    from google.oauth2 import service_account
    sa_json = os.environ.get("GSC_SERVICE_ACCOUNT_JSON", "").strip()
    if not sa_json:
        raise RuntimeError("missing GSC_SERVICE_ACCOUNT_JSON env var")
    sa_info = json.loads(sa_json)
    return service_account.Credentials.from_service_account_info(
        sa_info, scopes=scopes or ["https://www.googleapis.com/auth/analytics.readonly"]
    )

def run_report(property_id, start_date, end_date, dimensions, metrics, limit=10000):
    """Run a GA4 Analytics Data API report."""
    from googleapiclient.discovery import build
    creds = _get_creds()
    service = build("analyticsdata", "v1beta", credentials=creds, cache_discovery=False)
    body = {
        "dateRanges": [{"startDate": start_date, "endDate": end_date}],
        "dimensions": [{"name": d} for d in dimensions],
        "metrics": [{"name": m} for m in metrics],
        "limit": limit,
        "keepEmptyRows": False,
    }
    response = service.properties().runReport(property=f"properties/{property_id}", body=body).execute()
    return response

def parse_report(response):
    """Parse GA4 API response into list of dicts."""
    dim_headers = [h.get("name") for h in response.get("dimensionHeaders", [])]
    met_headers = [h.get("name") for h in response.get("metricHeaders", [])]
    rows = []
    for row in response.get("rows", []):
        entry = {}
        for i, dv in enumerate(row.get("dimensionValues", [])):
            if i < len(dim_headers):
                entry[dim_headers[i]] = dv.get("value", "")
        for i, mv in enumerate(row.get("metricValues", [])):
            if i < len(met_headers):
                try:
                    entry[met_headers[i]] = float(mv.get("value", 0))
                except ValueError:
                    entry[met_headers[i]] = mv.get("value", 0)
        rows.append(entry)
    return rows
