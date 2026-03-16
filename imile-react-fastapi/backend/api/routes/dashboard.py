"""
api/routes/dashboard.py — Dados do Dashboard principal
"""
from fastapi import APIRouter, Depends, Query
from api.deps import get_supabase, get_current_user
import pandas as pd
import numpy as np

router = APIRouter()


def _filter_bases(query, bases: list):
    if bases:
        query = query.in_("scan_station", bases)
    return query


@router.get("/datas")
def datas_disponiveis(user: dict = Depends(get_current_user)):
    sb = get_supabase()
    q = sb.table("expedicao_diaria").select("data_ref")
    if user["bases"]:
        q = q.in_("scan_station", user["bases"])
    res = q.execute()
    if not res.data:
        return []
    return sorted(set(r["data_ref"] for r in res.data), reverse=True)


@router.get("/dia/{data_ref}")
def dados_dia(data_ref: str, user: dict = Depends(get_current_user)):
    sb = get_supabase()
    q = sb.table("expedicao_diaria").select("*").eq("data_ref", data_ref)
    if user["bases"]:
        q = q.in_("scan_station", user["bases"])
    res = q.execute()
    data = res.data or []

    if not data:
        return {"kpis": {}, "stations": [], "alertas": []}

    df = pd.DataFrame(data)

    recebido = int(df["recebido"].sum())
    expedido = int(df["expedido"].sum())
    entregas = int(df["entregas"].sum())
    taxa_exp = round(expedido / recebido, 4) if recebido else 0
    taxa_ent = round(entregas / recebido, 4) if recebido else 0
    n_ds     = len(df)
    n_ok     = int(df["atingiu_meta"].sum())

    # Alertas — DS abaixo da meta
    df_alerta = df[df["taxa_exp"] < df["meta"]]
    alertas = df_alerta.sort_values("taxa_exp")["scan_station"].head(5).tolist()

    # Ranking
    ranking = (df[["scan_station","region","recebido","expedido","entregas",
                    "taxa_exp","taxa_ent","meta","atingiu_meta"]]
               .sort_values("taxa_exp", ascending=False)
               .to_dict("records"))

    return {
        "kpis": {
            "recebido":  recebido,
            "expedido":  expedido,
            "entregas":  entregas,
            "taxa_exp":  taxa_exp,
            "taxa_ent":  taxa_ent,
            "n_ds":      n_ds,
            "n_ok":      n_ok,
            "n_abaixo":  n_ds - n_ok,
        },
        "stations": ranking,
        "alertas": alertas,
        "ds_disponiveis": sorted(df["scan_station"].unique().tolist()),
    }


@router.get("/cidades/{data_ref}")
def cidades_dia(data_ref: str, user: dict = Depends(get_current_user)):
    sb = get_supabase()
    q = sb.table("expedicao_cidades").select("*").eq("data_ref", data_ref)
    if user["bases"]:
        q = q.in_("scan_station", user["bases"])
    res = q.execute()
    return res.data or []


@router.get("/charts/{data_ref}")
def chart_data(data_ref: str, user: dict = Depends(get_current_user)):
    """Dados formatados para os gráficos do frontend."""
    sb = get_supabase()
    q = sb.table("expedicao_diaria").select("*").eq("data_ref", data_ref)
    if user["bases"]:
        q = q.in_("scan_station", user["bases"])
    res = q.execute()

    if not res.data:
        return {"volume_ds": [], "taxa_ds": [], "donut": {}}

    df = pd.DataFrame(res.data).sort_values("recebido", ascending=False)

    volume_ds = [
        {
            "ds": r["scan_station"],
            "recebido": int(r["recebido"]),
            "expedido": int(r["expedido"]),
            "entregas": int(r["entregas"]),
        }
        for _, r in df.iterrows()
    ]

    taxa_ds = [
        {
            "ds": r["scan_station"],
            "taxa_exp": round(float(r["taxa_exp"]), 4),
            "meta": round(float(r["meta"]), 4),
            "atingiu": bool(r["atingiu_meta"]),
        }
        for _, r in df.sort_values("taxa_exp", ascending=True).iterrows()
    ]

    recebido = int(df["recebido"].sum())
    expedido = int(df["expedido"].sum())

    return {
        "volume_ds": volume_ds,
        "taxa_ds": taxa_ds,
        "donut": {
            "expedido": expedido,
            "backlog": max(recebido - expedido, 0),
            "taxa": round(expedido / recebido, 4) if recebido else 0,
        }
    }
