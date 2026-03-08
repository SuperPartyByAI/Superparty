import os
import logging
from typing import Dict, Any, Tuple
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build
import datetime

log = logging.getLogger("gsc_client")

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

def get_gsc_service():
    """
    Initializes the GSC service using Application Default Credentials explicitly constrained to Service Accounts.
    Expects GOOGLE_APPLICATION_CREDENTIALS environment variable.
    """
    if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
        log.error("GOOGLE_APPLICATION_CREDENTIALS environment variable is completely missing.")
        raise ValueError("Service Account explicitly required for L7 Cron operations.")

    try:
        credentials, project = google.auth.default(scopes=SCOPES)
        if not isinstance(credentials, service_account.Credentials):
            log.error("Loaded credentials are not of type ServiceAccountCredentials.")
            raise ValueError("Only Service Account authentication is allowed. User/ADC rejected.")
            
        service = build("searchconsole", "v1", credentials=credentials, cache_discovery=False)
        return service
    except Exception as e:
        log.error(f"Failed to initialize GSC client: {e}")
        raise

def fetch_search_analytics(property_uri: str, start_date: str, end_date: str, dimensions: list, row_limit: int = 5000) -> Dict[str, Any]:
    """
    Calls the Search Console API for a given property and date range.
    property_uri: e.g. 'sc-domain:superparty.ro'
    start_date, end_date: 'YYYY-MM-DD'
    """
    service = get_gsc_service()
    
    request_body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": dimensions,
        "rowLimit": row_limit
    }
    
    log.info(f"Querying GSC for {property_uri} from {start_date} to {end_date}...")
    response = service.searchanalytics().query(siteUrl=property_uri, body=request_body).execute()
    return response

def generate_gsc_date_range(days_lookback: int = 30, days_delay: int = 2) -> Tuple[str, str, int]:
    """
    Returns start_date, end_date in YYYY-MM-DD format and the actual interval covered.
    GSC data usually has a 2-day delay.
    """
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    end_dt = utc_now - datetime.timedelta(days=days_delay)
    start_dt = end_dt - datetime.timedelta(days=days_lookback - 1)
    
    return start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"), days_lookback
