
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi import Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.security import CurrentUser, get_current_user
from app.api.routes.tasks import router as tasks_router

app = FastAPI(
    title="TaskFlow API",
    description="API para gerenciamento de tarefas e produtividade.",
    version="0.1.0",
)

# Permite que o Angular local acesse a API durante o desenvolvimento.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(tasks_router)

@app.get("/", tags=["Health"])
def read_root():
    return {
        "message": "TaskFlow API está funcionando",
        "version": "0.1.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}




@app.get("/health/db", tags=["Health"])
def database_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"database": "connected"}
    except SQLAlchemyError:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível consultar o banco de dados.",
        )


@app.get("/auth/me", tags=["Authentication"])
def read_current_user(
    current_user: CurrentUser = Depends(get_current_user),
):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
    }