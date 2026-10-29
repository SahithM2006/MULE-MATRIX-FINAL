import pytest
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.models.entities import SyntheticInstitution, Account, Transaction, Alert
from app.services.scenario_generator import ScenarioGenerator

TEST_DB_PATH = settings.TEST_DATABASE_PATH
TEST_DB_URL = settings.TEST_DATABASE_URL

@pytest.fixture(scope="session")
def test_engine():
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            pass
    engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            pass

@pytest.fixture(scope="function")
def db_session(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        # Seed test institutions
        ScenarioGenerator.seed_institutions(session)
        yield session
    finally:
        session.rollback()
        session.close()

