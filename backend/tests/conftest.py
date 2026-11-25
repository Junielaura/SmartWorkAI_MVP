import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.core.security import get_current_user  # noqa: E402
from app.db.session import get_session  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Organization, User  # noqa: E402


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture()
def user(session):
    organization = Organization(name="Test Org", plan_type="free")
    session.add(organization)
    session.commit()
    session.refresh(organization)

    user = User(
        email="tester@example.com",
        password_hash="not-used",
        role="owner",
        organization_id=organization.id,
        organization_ids=[organization.id],
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture()
def client(engine, session, user, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_DIR", str(tmp_path / "storage"))
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path / "uploads"))
    monkeypatch.setattr(settings, "GENERATED_DIR", str(tmp_path / "generated"))
    monkeypatch.setattr(settings, "LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setattr(settings, "OLLAMA_HOST", "http://ollama:11434")
    monkeypatch.setattr(settings, "OLLAMA_TIMEOUT", 1)

    def override_session():
        yield session

    def override_user():
        return user

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_current_user] = override_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
