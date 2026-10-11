"""
Shared test fixtures.

These tests exercise API wiring and service-layer logic by mocking the
data-access layer (asyncpg calls) and the LLM provider — they do not
require a live Postgres/pgvector instance or network access to an LLM
API. That keeps them fast and runnable in CI, while still exercising the
real request/response schemas, validation rules, and pipeline logic
(caching keys, evidence-strength computation, gap filtering, etc).

Full integration testing against a real Supabase/pgvector database and a
real LLM is expected to be done manually against `.env` per the README's
demonstration procedure — that is explicitly out of scope for this
lightweight suite (see task requirement 25: "do not attempt to create an
enormous test suite").
"""
from __future__ import annotations

import sys
from unittest.mock import AsyncMock
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def mock_db_pool(monkeypatch):
    monkeypatch.setattr("app.core.database.init_pool", AsyncMock())
    monkeypatch.setattr("app.core.database.close_pool", AsyncMock())
    monkeypatch.setattr("app.main.init_pool", AsyncMock())
    monkeypatch.setattr("app.main.close_pool", AsyncMock())


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
