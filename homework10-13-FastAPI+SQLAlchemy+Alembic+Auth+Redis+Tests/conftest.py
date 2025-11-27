import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from models import Base

# Настройки для тестов
TEST_DATABASE_URL = "sqlite:///./test_students.db"


@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для асинхронных тестов"""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def engine():
    """Создание engine для тестовой БД"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    # Удаляем тестовую БД
    if os.path.exists("test_students.db"):
        os.remove("test_students.db")


@pytest.fixture(scope="function")
def db_session(engine):
    """Создание сессии для каждого теста"""
    connection = engine.connect()
    transaction = connection.begin()
    session = sessionmaker(bind=connection)()

    yield session

    session.close()
    transaction.rollback()
    connection.close()