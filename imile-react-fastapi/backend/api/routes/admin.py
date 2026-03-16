"""
api/routes/admin.py — Rotas administrativas
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from api.deps import get_supabase, get_supabase_admin, require_admin

router = APIRouter()


# ── Usuários ──────────────────────────────────────────────────
@router.get("/usuarios")
def listar_usuarios(user: dict = Depends(require_admin)):
    sb = get_supabase()
    res = sb.table("usuarios").select("*").order("nome").execute()
    return res.data or []


class PermissoesRequest(BaseModel):
    bases: list = []
    paginas: list = []
    role: str = "viewer"
    ativo: bool = True


@router.put("/usuarios/{user_id}")
def atualizar_usuario(user_id: str, req: PermissoesRequest, user: dict = Depends(require_admin)):
    sb = get_supabase()
    sb.table("usuarios").update({
        "bases":    req.bases,
        "paginas":  req.paginas,
        "role":     req.role,
        "ativo":    req.ativo,
        "atualizado_por": user["email"],
    }).eq("id", user_id).execute()
    return {"ok": True}


# ── Solicitações de Acesso ────────────────────────────────────
@router.get("/solicitacoes")
def listar_solicitacoes(status: str = "pendente", user: dict = Depends(require_admin)):
    sb = get_supabase()
    res = (sb.table("solicitacoes_acesso").select("*")
           .eq("status", status)
           .order("criado_em", desc=True).execute())
    return res.data or []


@router.post("/solicitacoes/{sol_id}/aprovar")
def aprovar(sol_id: int, role: str = "viewer", user: dict = Depends(require_admin)):
    sb = get_supabase()
    sb_admin = get_supabase_admin()

    sol = sb.table("solicitacoes_acesso").select("*").eq("id", sol_id).execute()
    if not sol.data:
        raise HTTPException(404, "Solicitação não encontrada")

    s = sol.data[0]
    sb.table("solicitacoes_acesso").update({"status": "aprovado"}).eq("id", sol_id).execute()

    # Convida no Auth
    auth_id = None
    try:
        invite = sb_admin.auth.admin.invite_user_by_email(s["email"])
        auth_id = invite.user.id if invite and invite.user else None
    except Exception:
        try:
            users = sb_admin.auth.admin.list_users()
            auth_id = next((u.id for u in users if u.email == s["email"]), None)
        except Exception:
            pass

    row = {"email": s["email"], "nome": s["nome"], "role": role, "bases": [], "ativo": True}
    if auth_id:
        row["id"] = auth_id
    sb.table("usuarios").upsert(row, on_conflict="email").execute()

    return {"ok": True}


@router.post("/solicitacoes/{sol_id}/rejeitar")
def rejeitar(sol_id: int, user: dict = Depends(require_admin)):
    sb = get_supabase()
    sb.table("solicitacoes_acesso").update({"status": "rejeitado"}).eq("id", sol_id).execute()
    return {"ok": True}


# ── Motoristas ────────────────────────────────────────────────
class MotoristaRequest(BaseModel):
    id_motorista: str
    nome_motorista: str = ""
    ativo: bool = True
    motivo: str = ""


@router.post("/motoristas")
def upsert_motorista(req: MotoristaRequest, user: dict = Depends(require_admin)):
    from datetime import datetime
    sb = get_supabase()
    sb.table("motoristas_status").upsert({
        "id_motorista":   req.id_motorista,
        "nome_motorista": req.nome_motorista,
        "ativo":          req.ativo,
        "motivo":         req.motivo,
        "atualizado_em":  datetime.utcnow().isoformat(),
        "atualizado_por": user["email"],
    }, on_conflict="id_motorista").execute()
    return {"ok": True}
