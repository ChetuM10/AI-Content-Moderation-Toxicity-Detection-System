"""MongoDB client utilities."""

from __future__ import annotations

import os
from typing import Optional

import mongomock
from pymongo import MongoClient
from pymongo.collection import Collection

# Cached client instance (real or mock depending on configuration)
_client: Optional[MongoClient] = None


def _should_use_mock() -> bool:
    """Determine whether to use an in-memory MongoDB mock."""
    return os.getenv("MONGO_USE_MOCK", "false").lower() == "true"


def get_client(uri: str) -> MongoClient:
    """Create a MongoClient or return the existing cached instance."""
    global _client
    if _client is None:
        if _should_use_mock():
            _client = mongomock.MongoClient()
        else:
            _client = MongoClient(uri)
    return _client


def get_database(uri: str, database_name: str):
    """Return a handle to the configured database."""
    client = get_client(uri)
    return client[database_name]


def get_collection(uri: str, database_name: str, collection_name: str) -> Collection:
    """Return a collection handle from the configured database."""
    database = get_database(uri, database_name)
    return database[collection_name]