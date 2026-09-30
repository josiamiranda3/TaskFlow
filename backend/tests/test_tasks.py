
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.db import Base
from app.core.dependencies import get_db
from app.core.security import CurrentUser, get_current_user
from app.main import app
from app.models.task import Task


TEST_USER_ID = uuid.uuid4()


@pytest.fixture
def db_session():
    # Banco SQLite isolado, mantido em memória durante cada teste.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        yield session

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    def override_get_current_user():
        return CurrentUser(
            id=TEST_USER_ID,
            email="teste@taskflow.local",
        )

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# =========================
# Testes de criação
# =========================

def test_create_task(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Estudar Python",
            "description": "Praticar testes automatizados",
            "priority": "high",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Estudar Python"
    assert data["description"] == "Praticar testes automatizados"
    assert data["status"] == "pending"
    assert data["priority"] == "high"
    assert data["user_id"] == str(TEST_USER_ID)
    assert data["id"] is not None


def test_create_task_with_invalid_priority(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Tarefa inválida",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422


def test_create_task_with_empty_title_returns_422(client):
    response = client.post(
        "/tasks",
        json={"title": ""},
    )

    assert response.status_code == 422


def test_create_task_with_invalid_status_returns_422(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Tarefa inválida",
            "status": "waiting",
        },
    )

    assert response.status_code == 422


# =========================
# Testes de listagem
# =========================

def test_list_only_current_users_tasks(client, db_session):
    other_user_id = uuid.uuid4()

    db_session.add(
        Task(
            user_id=other_user_id,
            title="Tarefa de outro usuário",
        )
    )
    db_session.commit()

    client.post(
        "/tasks",
        json={"title": "Minha tarefa"},
    )

    response = client.get("/tasks")

    assert response.status_code == 200

    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Minha tarefa"
    assert tasks[0]["user_id"] == str(TEST_USER_ID)


# =========================
# Testes de atualização
# =========================

def test_update_task(client):
    created = client.post(
        "/tasks",
        json={"title": "Título original"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "title": "Título atualizado",
            "status": "completed",
        },
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Título atualizado"
    assert response.json()["status"] == "completed"


def test_update_task_rejects_null_title(client):
    created = client.post(
        "/tasks",
        json={"title": "Tarefa válida"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": None},
    )

    assert response.status_code == 422


def test_update_nonexistent_task_returns_404(client):
    response = client.patch(
        f"/tasks/{uuid.uuid4()}",
        json={"title": "Nova tentativa"},
    )

    assert response.status_code == 404


def test_update_task_from_another_user_returns_404(client, db_session):
    other_user_task = Task(
        user_id=uuid.uuid4(),
        title="Tarefa privada",
    )
    db_session.add(other_user_task)
    db_session.commit()

    response = client.patch(
        f"/tasks/{other_user_task.id}",
        json={"title": "Tentativa de alteração"},
    )

    assert response.status_code == 404

    db_session.refresh(other_user_task)
    assert other_user_task.title == "Tarefa privada"


def test_update_task_description_and_due_date(client):
    created = client.post(
        "/tasks",
        json={"title": "Entregar projeto"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={
            "description": "Finalizar documentação",
            "due_date": "2027-01-15T18:00:00Z",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["description"] == "Finalizar documentação"
    assert data["due_date"] is not None
    assert data["due_date"].startswith("2027-01-15T18:00:00")


def test_update_task_with_invalid_priority_returns_422(client):
    created = client.post(
        "/tasks",
        json={"title": "Tarefa válida"},
    )
    task_id = created.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}",
        json={"priority": "urgent"},
    )

    assert response.status_code == 422


def test_invalid_task_uuid_returns_422(client):
    response = client.patch(
        "/tasks/uuid-invalido",
        json={"title": "Novo título"},
    )

    assert response.status_code == 422


# =========================
# Testes de exclusão
# =========================

def test_delete_task(client):
    created = client.post(
        "/tasks",
        json={"title": "Tarefa para excluir"},
    )
    task_id = created.json()["id"]

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 204

    list_response = client.get("/tasks")
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_delete_other_users_task_returns_404(client, db_session):
    other_user_task = Task(
        user_id=uuid.uuid4(),
        title="Tarefa privada",
    )
    db_session.add(other_user_task)
    db_session.commit()

    response = client.delete(f"/tasks/{other_user_task.id}")

    assert response.status_code == 404


# =========================
# Testes dos endpoints gerais
# =========================

def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "TaskFlow API está funcionando"
    )


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_database_health_endpoint(client):
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"database": "connected"}


def test_current_user_endpoint(client):
    response = client.get("/auth/me")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == str(TEST_USER_ID)
    assert data["email"] == "teste@taskflow.local"


# =========================
# Testes de falhas no banco
# =========================

def test_create_task_database_error_returns_500(client, monkeypatch):
    def fail_commit(self):
        raise SQLAlchemyError("Erro simulado no banco")

    monkeypatch.setattr(Session, "commit", fail_commit)

    response = client.post(
        "/tasks",
        json={"title": "Tarefa de teste"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Não foi possível criar a tarefa."
    )


def test_list_tasks_database_error_returns_500(client, monkeypatch):
    def fail_scalars(self, statement, *args, **kwargs):
        raise SQLAlchemyError("Erro simulado na consulta")

    monkeypatch.setattr(Session, "scalars", fail_scalars)

    response = client.get("/tasks")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Não foi possível listar as tarefas."
    )


def test_update_task_database_error_returns_500(client, monkeypatch):
    created = client.post(
        "/tasks",
        json={"title": "Tarefa para atualizar"},
    )
    assert created.status_code == 201

    task_id = created.json()["id"]

    def fail_commit(self):
        raise SQLAlchemyError("Erro simulado na atualização")

    monkeypatch.setattr(Session, "commit", fail_commit)

    response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Título atualizado"},
    )

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Não foi possível atualizar a tarefa."
    )


def test_delete_task_database_error_returns_500(client, monkeypatch):
    created = client.post(
        "/tasks",
        json={"title": "Tarefa para excluir"},
    )
    assert created.status_code == 201

    task_id = created.json()["id"]

    def fail_commit(self):
        raise SQLAlchemyError("Erro simulado na exclusão")

    monkeypatch.setattr(Session, "commit", fail_commit)

    response = client.delete(f"/tasks/{task_id}")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "Não foi possível excluir a tarefa."
    )