
import os
from uuid import UUID

import httpx
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")

if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
    raise RuntimeError(
        "Configure SUPABASE_URL e SUPABASE_PUBLISHABLE_KEY no arquivo .env."
    )

bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser(BaseModel):
    id: UUID
    email: str | None = None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação não informado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Esquema de autenticação inválido.",
        )

    headers = {
        "apikey": SUPABASE_PUBLISHABLE_KEY,
        "Authorization": f"Bearer {credentials.credentials}",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers=headers,
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Serviço de autenticação temporariamente indisponível.",
        )

    if response.status_code in (401, 403):
        raise HTTPException(
            status_code=401,
            detail="Token de autenticação inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if response.status_code >= 400:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível validar a autenticação.",
        )

    try:
        user_data = response.json()
        return CurrentUser(
            id=UUID(str(user_data["id"])),
            email=user_data.get("email"),
        )
    except (ValueError, TypeError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Resposta de autenticação inválida.",
        )