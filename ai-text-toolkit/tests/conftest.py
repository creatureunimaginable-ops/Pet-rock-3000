import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    from app import config, database
    from app.main import app

    db_path = tmp_path / "test.db"
    object.__setattr__(config.settings, "database_path", str(db_path))
    database._connection = None
    database.init_db()
    with TestClient(app) as test_client:
        yield test_client
    database._connection = None
