"""Shared plumbing for all fetchers: raw persistence, config, HTTP session."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests
import yaml

logger = logging.getLogger("bpc_intel.fetchers")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CONFIG_DIR = PROJECT_ROOT / "config"

DEFAULT_TIMEOUT = 30
USER_AGENT = "bpc-intel/1.0 (market research; contact: rohnit.agrawal@hec.edu)"


def session() -> requests.Session:
    """A requests session with the project user agent."""
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def save_raw(source: str, records: list | dict, output_dir: str | Path = RAW_DIR) -> Path:
    """Persist raw fetcher output as timestamped JSON.

    Args:
        source: Short source key, e.g. "comtrade".
        records: The raw payload.
        output_dir: Directory for raw files (default data/raw/).

    Returns:
        Path to the file written.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = output_dir / f"{source}_{stamp}.json"
    path.write_text(
        json.dumps({"source": source, "fetched_at": stamp, "records": records},
                   indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    logger.info("Saved raw %s output to %s", source, path)
    return path


def load_yaml(name: str) -> dict:
    """Load a config YAML by filename from config/.

    Args:
        name: e.g. "corridor.yaml".

    Returns:
        Parsed YAML dict (empty dict if the file is empty).
    """
    with (CONFIG_DIR / name).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_api_key(key_name: str) -> str | None:
    """Read an API key from config/api_keys.yaml if it exists.

    Args:
        key_name: Key within the YAML, e.g. "dart".

    Returns:
        The key string, or None if unconfigured.
    """
    path = CONFIG_DIR / "api_keys.yaml"
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as fh:
        keys = yaml.safe_load(fh) or {}
    value = keys.get(key_name)
    return value if value and not str(value).startswith("YOUR_") else None


__all__ = ["session", "save_raw", "load_yaml", "load_api_key",
           "DEFAULT_TIMEOUT", "PROJECT_ROOT", "RAW_DIR"]
