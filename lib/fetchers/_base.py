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


def _read_key_file() -> dict:
    """Parse config/api_keys.yaml (empty dict if absent)."""
    path = CONFIG_DIR / "api_keys.yaml"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _clean_key(value: object) -> str | None:
    """A usable key string, or None if unset or still a `YOUR_...` placeholder."""
    return str(value) if value and not str(value).startswith("YOUR_") else None


def load_api_key(key_name: str) -> str | None:
    """Read a single API key from config/api_keys.yaml if it exists.

    Args:
        key_name: Key within the YAML, e.g. "dart".

    Returns:
        The key string, or None if unconfigured or placeholder.
    """
    return _clean_key(_read_key_file().get(key_name))


def load_api_keys(key_name: str) -> list[str]:
    """Read a primary key plus an optional fallback, in priority order.

    Looks up ``<key_name>`` then ``<key_name>_fallback`` in
    config/api_keys.yaml, dropping any unset or placeholder value. Used by
    fetchers that fail over to a second key when the first is rate-limited or
    deactivated (e.g. DART, whose free tier caps daily calls per key).

    Args:
        key_name: Base key name, e.g. "dart" (also reads "dart_fallback").

    Returns:
        Configured keys, primary first. Empty list if none are set.
    """
    keys = _read_key_file()
    ordered: list[str] = []
    for name in (key_name, f"{key_name}_fallback"):
        cleaned = _clean_key(keys.get(name))
        if cleaned:
            ordered.append(cleaned)
    return ordered


__all__ = ["session", "save_raw", "load_yaml", "load_api_key", "load_api_keys",
           "DEFAULT_TIMEOUT", "PROJECT_ROOT", "RAW_DIR"]
