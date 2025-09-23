from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional, Protocol
from dataclasses import dataclass, field
import threading
import time


class FeatureBackend(Protocol):
    def get(self, key: str, default: Optional[Any] = None) -> Any: ...
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None: ...
    def mget(self, keys: Iterable[str]) -> Dict[str, Any]: ...
    def mset(self, items: Mapping[str, Any], ttl_seconds: Optional[int] = None) -> None: ...


@dataclass
class _Item:
    value: Any
    expires_at: Optional[float] = None


class InMemoryBackend(FeatureBackend):
    """Thread-safe, TTL-aware in-memory store for small/medium deployments."""
    def __init__(self) -> None:
        self._data: Dict[str, _Item] = {}
        self._lock = threading.RLock()

    def _prune(self) -> None:
        now = time.time()
        to_delete = [k for k, v in self._data.items() if v.expires_at and v.expires_at <= now]
        for k in to_delete:
            del self._data[k]

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        with self._lock:
            self._prune()
            item = self._data.get(key)
            return default if item is None else item.value

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        with self._lock:
            expires_at = time.time() + ttl_seconds if ttl_seconds else None
            self._data[key] = _Item(value=value, expires_at=expires_at)

    def mget(self, keys: Iterable[str]) -> Dict[str, Any]:
        with self._lock:
            self._prune()
            return {k: self._data[k].value for k in keys if k in self._data}

    def mset(self, items: Mapping[str, Any], ttl_seconds: Optional[int] = None) -> None:
        with self._lock:
            expires_at = time.time() + ttl_seconds if ttl_seconds else None
            for k, v in items.items():
                self._data[k] = _Item(value=v, expires_at=expires_at)


@dataclass
class FeatureStore:
    backend: FeatureBackend = field(default_factory=InMemoryBackend)

    def feature_key(self, *parts: str) -> str:
        return ":".join(parts)

    def put_features(self, namespace: str, entity_id: str, feats: Mapping[str, Any], ttl_seconds: Optional[int] = 3600) -> None:
        namespaced = {self.feature_key(namespace, entity_id, k): v for k, v in feats.items()}
        self.backend.mset(namespaced, ttl_seconds=ttl_seconds)

    def get_features(self, namespace: str, entity_id: str, names: Iterable[str]) -> Dict[str, Any]:
        keys = [self.feature_key(namespace, entity_id, n) for n in names]
        return self.backend.mget(keys)
