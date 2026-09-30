
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


def get_required_env(name: str) -> str:
    """Obtém uma variável de ambiente obrigatória."""
    value = os.getenv(name)

    if not value:
        raise RuntimeError(
            f"A variável de ambiente obrigatória '{name}' não foi configurada."
        )

    return value


database_url = URL.create(
    drivername="postgresql+psycopg",
    username=get_required_env("DB_USER"),
    password=get_required_env("DB_PASSWORD"),
    host=get_required_env("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "postgres"),
    query={"sslmode": os.getenv("DB_SSLMODE", "require")},
)

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=2,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def test_connection() -> str:
    """Verifica a conexão com o PostgreSQL."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    except SQLAlchemyError as exc:
        raise RuntimeError(
            "Não foi possível estabelecer conexão com o PostgreSQL. "
            "Verifique as configurações do banco e a conectividade."
        ) from exc

    return "Conexão com PostgreSQL estabelecida."