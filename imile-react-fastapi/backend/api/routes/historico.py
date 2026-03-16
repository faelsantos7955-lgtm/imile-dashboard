"""
api/routes/historico.py — Dados históricos por período
"""
from fastapi import APIRouter, Depends, Query
from api.deps import get_supabase, get_current_user
import pandas as pd
import numpy as np

router = APIRouter()


@router.get("/periodo")
def periodo(
    data_ini: str = Query(...),
    data_fim: str = Query(...),
    user: dict = Depends(get_current_user),
):
    sb = get_supabase()
    q = (sb.table("expedicao_diaria").select("*")
         .gte("data_ref", data_ini)
         .lte("data_ref", data_fim))
    if user["bases"]:
        q = q.in_("scan_station", user["bases"])
    res = q.execute()
    data = res.data or []

    if not data:
        return {"resumo": {}, "por_dia": [], "por_ds": []}

    df = pd.DataFrame(data)

    # Resumo
    rec = int(df["recebido"].sum())
    exp = int(df["expedido"].sum())
    ent = int(df["entregas"].sum())
    taxa = round(exp / rec, 4) if rec else 0
    dias = df["data_ref"].nunique()

    # Por dia
    por_dia = (df.groupby("data_ref", as_index=False)
               .agg(recebido=("recebido","sum"),
                    expedido=("expedido","sum"),
                    entregas=("entregas","sum")))
    por_dia["taxa_exp"] = np.where(por_dia["recebido"]>0,
        (por_dia["expedido"]/por_dia["recebido"]).round(4), 0)
    por_dia = por_dia.sort_values("data_ref").to_dict("records")

    # Por DS
    por_ds = (df.groupby(["scan_station","region"], as_index=False)
              .agg(recebido=("recebido","sum"),
                   expedido=("expedido","sum"),
                   entregas=("entregas","sum")))
    por_ds["taxa_exp"] = np.where(por_ds["recebido"]>0,
        (por_ds["expedido"]/por_ds["recebido"]).round(4), 0)
    por_ds = por_ds.sort_values("recebido", ascending=False).to_dict("records")

    return {
        "resumo": {
            "recebido": rec, "expedido": exp, "entregas": ent,
            "taxa_exp": taxa, "dias": dias,
        },
        "por_dia": por_dia,
        "por_ds": por_ds,
    }
