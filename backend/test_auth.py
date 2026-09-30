
import os
from getpass import getpass

import httpx
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_PUBLISHABLE_KEY = os.environ["SUPABASE_PUBLISHABLE_KEY"]


def main():
    email = input("E-mail do usuário de teste: ").strip()
    password = getpass("Senha do usuário de teste: ")

    headers = {"apikey": SUPABASE_PUBLISHABLE_KEY}

    try:
        with httpx.Client(timeout=15.0) as client:
            # 1. Fazer login no Supabase Auth.
            login_response = client.post(
                f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
                headers=headers,
                json={"email": email, "password": password},
            )

            if login_response.status_code != 200:
                print("Falha no login.")
                print("Status HTTP:", login_response.status_code)
                print("Resposta:", login_response.text)
                return

            access_token = login_response.json()["access_token"]
            print("Login no Supabase realizado com sucesso.")

            # 2. Consultar a rota protegida da FastAPI.
            api_response = client.get(
                "http://127.0.0.1:8000/auth/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )

            print("Status da API:", api_response.status_code)

            if api_response.status_code == 200:
                user = api_response.json()
                print("Autenticação na FastAPI confirmada.")
                print("ID do usuário:", user["id"])
                print("E-mail retornado:", user.get("email"))
            else:
                print("A API não confirmou a autenticação.")
                print("Resposta:", api_response.text)

    except httpx.RequestError:
        print(
            "Não foi possível conectar ao Supabase ou à FastAPI. "
            "Verifique a conexão e se o servidor está ativo."
        )


if __name__ == "__main__":
    main()