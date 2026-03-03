"""site_loader.py - Load and validate site configurations."""
import logging
from pathlib import Path

log = logging.getLogger(__name__)

SITES_DIR = Path("agent/sites")


def load_sites():
    """Load all enabled site configs from agent/sites/*.yml."""
    try:
        import yaml
        HAS_YAML = True
    except ImportError:
        HAS_YAML = False

    sites = []
    if not SITES_DIR.exists():
        log.warning("agent/sites/ directory not found")
        return [{"site_id": "superparty"}]  # fallback

    for yml_path in sorted(SITES_DIR.glob("*.yml")):
        if yml_path.name == "schema.yml":
            continue
        try:
            if HAS_YAML:
                import yaml
                data = yaml.safe_load(yml_path.read_text(encoding="utf-8"))
            else:
                # Minimal YAML parser for simple key: value pairs
                data = {}
                for line in yml_path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and ":" in line:
                        k, _, v = line.partition(":")
                        data[k.strip()] = v.strip().strip('"').strip("'")

            if not data.get("site_id"):
                log.warning("Skipping %s: no site_id", yml_path.name)
                continue

            sites.append(data)
            log.info("Loaded site: %s", data["site_id"])
        except Exception as e:
            log.error("Failed loading %s: %s", yml_path.name, e)

    return sites or [{"site_id": "superparty"}]  # always have at least one


def get_site(site_id):
    """Get a specific site config by ID."""
    for site in load_sites():
        if site.get("site_id") == site_id:
            return site
    return {"site_id": site_id}  # minimal fallback
