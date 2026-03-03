"""github_app_token.py - Generate GitHub App installation token at runtime.

Usage:
    token = get_installation_token()
    # use token for GitHub API calls (valid ~1h)

Requires env vars:
    GITHUB_APP_ID          Numeric App ID
    GITHUB_APP_PRIVATE_KEY Base64-encoded PEM private key (or set GITHUB_APP_PRIVATE_KEY_PATH)
    GITHUB_INSTALLATION_ID Numeric installation ID

Falls back to GITHUB_TOKEN if App credentials not configured.
"""
import base64
import json
import logging
import os
import time
import urllib.error
import urllib.request

log = logging.getLogger(__name__)

_token_cache: dict = {}  # {"token": str, "expires_at": float}


def _make_jwt(app_id: str, private_key_pem: str) -> str:
    """Create a JWT for GitHub App authentication."""
    # Minimal JWT without external deps (using RS256 via cryptography if available)
    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
        import struct

        now = int(time.time())
        header = base64.urlsafe_b64encode(
            json.dumps({"alg": "RS256", "typ": "JWT"}).encode()
        ).rstrip(b"=")
        payload = base64.urlsafe_b64encode(
            json.dumps({"iat": now - 60, "exp": now + 540, "iss": app_id}).encode()
        ).rstrip(b"=")
        msg = header + b"." + payload

        key = serialization.load_pem_private_key(private_key_pem.encode(), password=None)
        signature = key.sign(msg, padding.PKCS1v15(), hashes.SHA256())
        sig_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=")
        return (msg + b"." + sig_b64).decode()
    except ImportError:
        raise RuntimeError(
            "cryptography package required for GitHub App JWT. "
            "Install: pip install cryptography"
        )


def get_installation_token() -> str:
    """Get a GitHub App installation token (cached, refreshed before expiry).

    Falls back to GITHUB_TOKEN env var if App credentials not set.
    """
    # Fallback: use PAT if App not configured
    app_id = os.environ.get("GITHUB_APP_ID", "")
    installation_id = os.environ.get("GITHUB_INSTALLATION_ID", "")

    if not app_id or not installation_id:
        token = os.environ.get("GITHUB_TOKEN", "")
        if token:
            log.debug("GitHub App not configured, using GITHUB_TOKEN PAT")
            return token
        raise RuntimeError(
            "Neither GITHUB_APP_ID/GITHUB_INSTALLATION_ID nor GITHUB_TOKEN is set"
        )

    # Check cache
    cached = _token_cache.get("token")
    expires_at = _token_cache.get("expires_at", 0)
    if cached and time.time() < expires_at - 60:
        return cached

    # Load private key
    pem_b64 = os.environ.get("GITHUB_APP_PRIVATE_KEY", "")
    pem_path = os.environ.get("GITHUB_APP_PRIVATE_KEY_PATH", "")
    if pem_path:
        from pathlib import Path
        private_key_pem = Path(pem_path).read_text()
    elif pem_b64:
        private_key_pem = base64.b64decode(pem_b64).decode()
    else:
        raise RuntimeError(
            "Set GITHUB_APP_PRIVATE_KEY (base64) or GITHUB_APP_PRIVATE_KEY_PATH"
        )

    jwt_token = _make_jwt(app_id, private_key_pem)

    # Exchange JWT for installation token
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    h = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "superparty-agent",
    }
    req = urllib.request.Request(url, method="POST", headers=h)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Failed to get installation token: {e.code} {e.read()[:200]}")

    token = data["token"]
    expires_at_str = data.get("expires_at", "")
    # parse ISO 8601
    try:
        import datetime
        dt = datetime.datetime.fromisoformat(expires_at_str.replace("Z", "+00:00"))
        _token_cache["expires_at"] = dt.timestamp()
    except Exception:
        _token_cache["expires_at"] = time.time() + 3600

    _token_cache["token"] = token
    log.info("GitHub App installation token acquired (expires at %s)", expires_at_str)
    return token
