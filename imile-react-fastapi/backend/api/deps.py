"""
api/deps.py — Dependências compartilhadas (Supabase client, auth)
"""
import os
from functools import lru_cache
from fastapi import Depends, HTTPException, Header
from supabase import create_client, Client


@lru_cache()
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL e SUPABASE_KEY não configurados")
    return create_client(url, key)


@lru_cache()
def get_supabase_admin() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_KEY", ""))
    return create_client(url, key)


async def get_current_user(authorization: str = Header(None)) -> dict:
    """Extrai e valida o usuário a partir do token JWT do Supabase."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token não fornecido")

    token = authorization.replace("Bearer ", "")
    sb = get_supabase()

    try:
        user_res = sb.auth.get_user(token)
        if not user_res or not user_res.user:
            raise HTTPException(status_code=401, detail="Token inválido")

        user = user_res.user

        # Busca perfil na tabela usuarios
        perfil = sb.table("usuarios").select("*").eq("id", str(user.id)).execute()
        if not perfil.data:
            perfil = sb.table("usuarios").select("*").eq("email", user.email).execute()

        if not perfil.data:
            raise HTTPException(status_code=403, detail="Usuário sem perfil no portal")

        p = perfil.data[0]
        if not p.get("ativo", True):
            raise HTTPException(status_code=403, detail="Conta desativada")

        return {
            "id":       str(user.id),
            "email":    user.email,
            "nome":     p.get("nome", ""),
            "role":     p.get("role", "viewer"),
            "bases":    p.get("bases") or [],
            "paginas":  p.get("paginas") or [],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erro de autenticação: {e}")


def require_admin(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito ao administrador")
    return user
