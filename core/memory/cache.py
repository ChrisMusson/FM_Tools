"""Small disk-backed cache helpers for repeated FM memory scans."""

import hashlib
import json
import os
import pickle
import time
from pathlib import Path

from core.memory.session import read_game_cache_fingerprint

DEFAULT_CACHE_LIFETIME_SECONDS = 300
CACHE_DIR = Path(".cache") / "fm_memory"
CACHE_VERSION = 1
_RUNTIME_CACHE = {}
_CACHE_MISS = object()


def get_cache_lifetime_seconds():
    return int(os.getenv("FM_CACHE_LIFETIME_SECONDS", os.getenv("FM_CACHE_TTL_SECONDS", DEFAULT_CACHE_LIFETIME_SECONDS)))


def _normalise_key_part(value):
    if isinstance(value, dict):
        return {str(key): _normalise_key_part(val) for key, val in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_normalise_key_part(item) for item in value]
    if isinstance(value, set):
        return sorted(_normalise_key_part(item) for item in value)
    return value


def _build_cache_context(process, namespace, key_parts):
    payload = {
        "version": CACHE_VERSION,
        "namespace": namespace,
        "fingerprint": read_game_cache_fingerprint(process),
        "key_parts": _normalise_key_part(key_parts),
    }
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    digest = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    return payload_json, CACHE_DIR / namespace / f"{digest}.pkl"


def _format_duration(seconds):
    seconds = max(0, int(seconds))
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def _runtime_get(runtime_key, now):
    cached = _RUNTIME_CACHE.get(runtime_key)
    if cached is None:
        return _CACHE_MISS

    expires_at, value = cached
    if now >= expires_at:
        _RUNTIME_CACHE.pop(runtime_key, None)
        return _CACHE_MISS
    return value, expires_at


def _runtime_set(runtime_key, value, lifetime_seconds, now):
    _RUNTIME_CACHE[runtime_key] = (now + lifetime_seconds, value)


def _disk_get(path, lifetime_seconds, now):
    try:
        stat = path.stat()
    except FileNotFoundError:
        return _CACHE_MISS

    age_seconds = now - stat.st_mtime
    if age_seconds > lifetime_seconds:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        return _CACHE_MISS

    try:
        with path.open("rb") as cache_file:
            return pickle.load(cache_file), age_seconds
    except Exception:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        return _CACHE_MISS


def _prune_namespace(namespace, lifetime_seconds, now):
    namespace_dir = CACHE_DIR / namespace
    if not namespace_dir.exists():
        return

    for path in namespace_dir.glob("*.pkl"):
        try:
            if now - path.stat().st_mtime > lifetime_seconds:
                path.unlink()
        except FileNotFoundError:
            continue


def _disk_set(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("wb") as cache_file:
        pickle.dump(value, cache_file, protocol=pickle.HIGHEST_PROTOCOL)
    tmp_path.replace(path)


def _log_cache_hit(namespace, source, detail):
    print(f"[cache] Hit {namespace} from {source} ({detail})")


def get_cached_or_compute(process, namespace, key_parts, builder, *, refresh=False):
    lifetime_seconds = get_cache_lifetime_seconds()
    now = time.time()

    try:
        runtime_key, path = _build_cache_context(process, namespace, key_parts)
    except Exception:
        return builder(), False

    if not refresh:
        cached = _runtime_get(runtime_key, now)
        if cached is not _CACHE_MISS:
            value, expires_at = cached
            _log_cache_hit(namespace, "memory", f"expires in {_format_duration(expires_at - now)}")
            return value, True

        cached = _disk_get(path, lifetime_seconds, now)
        if cached is not _CACHE_MISS:
            value, age_seconds = cached
            _runtime_set(runtime_key, value, lifetime_seconds, now)
            _log_cache_hit(namespace, "disk", f"age {_format_duration(age_seconds)}, expires after {_format_duration(lifetime_seconds)}")
            return value, True

    value = builder()
    _disk_set(path, value)
    _runtime_set(runtime_key, value, lifetime_seconds, now)
    _prune_namespace(namespace, lifetime_seconds, now)
    return value, False
