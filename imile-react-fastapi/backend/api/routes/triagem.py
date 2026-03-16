"""
api/routes/triagem.py — Dados de triagem
"""
from fastapi import APIRouter, Depends
from api.deps import get_supabase, get_current_user

router = APIRouter()


@router.get("/uploads")
def listar_uploads(user: dict = Depends(get_current_user)):
    sb = get_supabase()
    res = (sb.table("triagem_uploads")
           .select("id,data_ref,criado_por,total,qtd_ok,qtd_erro,taxa")
           .order("criado_em", desc=True).limit(30).execute())
    return res.data or []


@router.get("/upload/{upload_id}")
def detalhe_upload(upload_id: int, user: dict = Depends(get_current_user)):
    sb = get_supabase()

    r_ds  = sb.table("triagem_por_ds").select("*").eq("upload_id", upload_id).execute().data or []
    top5  = sb.table("triagem_top5").select("*").eq("upload_id", upload_id).order("total_erros", desc=True).execute().data or []
    r_sup = sb.table("triagem_por_supervisor").select("*").eq("upload_id", upload_id).execute().data or []

    return {
        "por_ds": r_ds,
        "top5": top5,
        "por_supervisor": r_sup,
    }
