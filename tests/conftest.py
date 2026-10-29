import os
import uuid

import pytest


@pytest.fixture
def pg_conn():
    """Connection to TEST_DATABASE_URL, isolated in a throwaway schema.

    Without TEST_DATABASE_URL the test is skipped, unless
    REQUIRE_TEST_DATABASE=1 (as in CI), which turns the skip into a failure.
    """
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        if os.environ.get("REQUIRE_TEST_DATABASE") == "1":
            pytest.fail("TEST_DATABASE_URL is not set but REQUIRE_TEST_DATABASE=1")
        pytest.skip("TEST_DATABASE_URL is not set")
    psycopg = pytest.importorskip("psycopg")

    schema = f"test_{uuid.uuid4().hex[:12]}"
    with psycopg.connect(url, autocommit=True) as conn:
        conn.execute(f"CREATE SCHEMA {schema}")
        conn.execute(f"SET search_path TO {schema}")
        try:
            yield conn
        finally:
            conn.execute(f"DROP SCHEMA {schema} CASCADE")
