"""
database.py — Integração com Supabase
Tabelas necessárias (criar no Supabase SQL Editor):

CREATE TABLE expedicao_diaria (
    id            BIGSERIAL PRIMARY KEY,
    data_ref      DATE        NOT NULL,
    scan_station  TEXT        NOT NULL,
    region        TEXT,
    recebido      INTEGER     DEFAULT 0,
    expedido      INTEGER     DEFAULT 0,
    entregas      INTEGER     DEFAULT 0,
    taxa_exp      FLOAT       DEFAULT 0,
    taxa_ent      FLOAT       DEFAULT 0,
    meta          FLOAT       DEFAULT 0.5,
    atingiu_meta  BOOLEAN     DEFAULT FALSE,
    processado_em TIMESTAMPTZ DEFAULT NOW(),
    processado_por TEXT,
    UNIQUE (data_ref, scan_station)
);

CREATE TABLE expedicao_cidades (
    id              BIGSERIAL PRIMARY KEY,
    data_ref        DATE  NOT NULL,
    scan_station    TEXT  NOT NULL,
    destination_city TEXT NOT NULL,
    recebido        INTEGER DEFAULT 0,
    expedido        INTEGER DEFAULT 0,
    entregas        INTEGER DEFAULT 0,
    taxa_exp        FLOAT   DEFAULT 0,
    taxa_ent        FLOAT   DEFAULT 0,
    UNIQUE (data_ref, scan_station, destination_city)
);

-- Habilitar RLS (Row Level Security) para separar por usuário/região
ALTER TABLE expedicao_diaria  ENABLE ROW LEVEL SECURITY;
ALTER TABLE expedicao_cidades ENABLE ROW LEVEL SECURITY;
"""

import os
import streamlit as st
from supabase import create_client, Client
import pandas as pd
from datetime import date, timedelta

# ── Conexão ───────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

# ══════════════════════════════════════════════════════════════
#  SALVAR
# ══════════════════════════════════════════════════════════════
def salvar_processamento(pivot_metricas: pd.DataFrame,
                          pivot_cidades: pd.DataFrame,
                          data_ref: date,
                          usuario: str):
    """Upsert dos resultados do dia no Supabase."""
    sb = get_supabase()

    # ── Tabela diária ─────────────────────────────────────────
    rows_diario = []
    for _, r in pivot_metricas.iterrows():
        rows_diario.append({
            "data_ref":      str(data_ref),
            "scan_station":  r["Scan Station"],
            "region":        r.get("REGION", ""),
            "recebido":      int(r.get("recebido no DS", 0)),
            "expedido":      int(r.get("em rota de entrega", 0)),
            "entregas":      int(r.get("Entregas", 0)),
            "taxa_exp":      float(r.get("Taxa de Expedicao", 0)),
            "taxa_ent":      float(r.get("Taxa de Entrega", 0)),
            "meta":          float(r.get("Meta", 0.5)),
            "atingiu_meta":  bool(r.get("Atingiu Meta", False)),
            "processado_por": usuario,
        })
    if rows_diario:
        sb.table("expedicao_diaria").upsert(
            rows_diario,
            on_conflict="data_ref,scan_station"
        ).execute()

    # ── Tabela cidades ────────────────────────────────────────
    rows_cidades = []
    for _, r in pivot_cidades.iterrows():
        rows_cidades.append({
            "data_ref":         str(data_ref),
            "scan_station":     r["Scan Station"],
            "destination_city": r["Destination City"],
            "recebido":         int(r.get("recebido no DS", 0)),
            "expedido":         int(r.get("em rota de entrega", 0)),
            "entregas":         int(r.get("Entregas", 0)),
            "taxa_exp":         float(r.get("Taxa de Expedicao", 0)),
            "taxa_ent":         float(r.get("Taxa de Entrega", 0)),
        })
    if rows_cidades:
        sb.table("expedicao_cidades").upsert(
            rows_cidades,
            on_conflict="data_ref,scan_station,destination_city"
        ).execute()

# ══════════════════════════════════════════════════════════════
#  LER
# ══════════════════════════════════════════════════════════════
def _filtrar_regioes(regioes_permitidas: list) -> list:
    """Retorna filtro de regiões para a query."""
    return regioes_permitidas  # lista de strings, ex: ["capital","metropolitan"]

@st.cache_data(ttl=300)  # cache 5 minutos
def ler_dia(data_ref: date, bases: list = None) -> pd.DataFrame:
    sb = get_supabase()
    q = sb.table("expedicao_diaria").select("*").eq("data_ref", str(data_ref))
    if bases:
        q = q.in_("scan_station", bases)
    res = q.execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

@st.cache_data(ttl=300)
def ler_periodo(data_ini: date, data_fim: date, bases: list = None) -> pd.DataFrame:
    sb = get_supabase()
    q = (sb.table("expedicao_diaria").select("*")
           .gte("data_ref", str(data_ini))
           .lte("data_ref", str(data_fim)))
    if bases:
        q = q.in_("scan_station", bases)
    res = q.execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

def ler_cidades_dia(data_ref: date, bases: list = None) -> pd.DataFrame:
    sb = get_supabase()
    q = sb.table("expedicao_cidades").select("*").eq("data_ref", str(data_ref))
    if bases:
        q = q.in_("scan_station", bases)
    res = q.execute()
    return pd.DataFrame(res.data) if res.data else pd.DataFrame()

@st.cache_data(ttl=300)
def ler_datas_disponiveis(bases: list = None) -> list:
    sb = get_supabase()
    q = sb.table("expedicao_diaria").select("data_ref")
    if bases:
        q = q.in_("scan_station", bases)
    res = q.execute()
    if not res.data:
        return []
    datas = sorted(set(r["data_ref"] for r in res.data), reverse=True)
    return datas

def invalidar_cache():
    """Limpa o cache do Streamlit para forçar releitura do banco."""
    ler_dia.clear()
    ler_periodo.clear()
    ler_datas_disponiveis.clear()


# ══════════════════════════════════════════════════════════════
#  ARQUIVOS FIXOS — Supervisores e Metas
#
#  SQL para criar as tabelas (rodar no Supabase SQL Editor):
#
#  CREATE TABLE config_supervisores (
#      id           BIGSERIAL PRIMARY KEY,
#      sigla        TEXT NOT NULL UNIQUE,
#      region       TEXT NOT NULL,
#      atualizado_em TIMESTAMPTZ DEFAULT NOW(),
#      atualizado_por TEXT
#  );
#
#  CREATE TABLE config_metas (
#      id           BIGSERIAL PRIMARY KEY,
#      ds           TEXT NOT NULL UNIQUE,
#      meta         FLOAT NOT NULL DEFAULT 0.5,
#      atualizado_em TIMESTAMPTZ DEFAULT NOW(),
#      atualizado_por TEXT
#  );
# ══════════════════════════════════════════════════════════════

import pandas as pd
from datetime import datetime

# ── Supervisores ──────────────────────────────────────────────
def salvar_supervisores(df: pd.DataFrame, usuario: str):
    """Faz upsert da tabela de supervisores no Supabase."""
    sb = get_supabase()
    rows = []
    for _, r in df.iterrows():
        sigla = str(r.get("SIGLA", "")).strip().upper()
        region = str(r.get("REGION", "")).strip()
        if sigla:
            rows.append({
                "sigla":          sigla,
                "region":         region,
                "atualizado_por": usuario,
            })
    if rows:
        sb.table("config_supervisores").upsert(
            rows, on_conflict="sigla"
        ).execute()

def carregar_supervisores() -> pd.DataFrame:
    """Lê supervisores do Supabase e retorna DataFrame com SIGLA e REGION."""
    sb = get_supabase()
    res = sb.table("config_supervisores").select("sigla,region").execute()
    if not res.data:
        return pd.DataFrame()
    df = pd.DataFrame(res.data)
    df.columns = ["SIGLA", "REGION"]
    return df

def tem_supervisores() -> bool:
    """Retorna True se já há supervisores salvos no banco."""
    sb = get_supabase()
    res = sb.table("config_supervisores").select("id").limit(1).execute()
    return bool(res.data)

# ── Metas ─────────────────────────────────────────────────────
def salvar_metas(df: pd.DataFrame, usuario: str):
    """Faz upsert da tabela de metas no Supabase."""
    sb = get_supabase()
    rows = []
    for _, r in df.iterrows():
        ds   = str(r.get("DS", "")).strip().upper()
        meta = float(r.get("Meta", 0.5))
        if ds:
            rows.append({
                "ds":             ds,
                "meta":           meta,
                "atualizado_por": usuario,
            })
    if rows:
        sb.table("config_metas").upsert(
            rows, on_conflict="ds"
        ).execute()

def carregar_metas() -> pd.DataFrame:
    """Lê metas do Supabase e retorna DataFrame com DS e Meta."""
    sb = get_supabase()
    res = sb.table("config_metas").select("ds,meta").execute()
    if not res.data:
        return pd.DataFrame()
    df = pd.DataFrame(res.data)
    df.columns = ["DS", "Meta"]
    return df

def tem_metas() -> bool:
    """Retorna True se já há metas salvas no banco."""
    sb = get_supabase()
    res = sb.table("config_metas").select("id").limit(1).execute()
    return bool(res.data)


# ══════════════════════════════════════════════════════════════
#  USUÁRIOS
# ══════════════════════════════════════════════════════════════
def get_user_meta(user_id: str) -> dict:
    """Busca perfil do usuário na tabela usuarios."""
    try:
        sb  = get_supabase()
        res = sb.table("usuarios").select("*").eq("id", user_id).execute()
        if res.data:
            return res.data[0]
        return {}
    except Exception:
        return {}

def listar_solicitacoes(status: str = "pendente") -> list:
    """Lista solicitações de acesso por status."""
    try:
        sb  = get_supabase()
        res = (sb.table("solicitacoes_acesso")
                 .select("*")
                 .eq("status", status)
                 .order("criado_em", desc=True)
                 .execute())
        return res.data or []
    except Exception:
        return []

def aprovar_solicitacao(sol_id: int, email: str, nome: str,
                         regiao: str, role: str = "viewer") -> tuple:
    """
    Aprova solicitação: cria usuário no Supabase Auth + insere em usuarios.
    Retorna (ok, erro)
    """
    try:
        sb = get_supabase()
        # Atualiza status da solicitação
        sb.table("solicitacoes_acesso").update(
            {"status": "aprovado"}
        ).eq("id", sol_id).execute()

        # Insere na tabela usuarios (o usuário cria a própria senha pelo email)
        regioes = ([regiao.lower()] if regiao.lower() not in ["todas", "todas as regiões", ""]
                   else ["capital", "metropolitan", "countryside"])
        sb.table("usuarios").upsert({
            "email":   email,
            "nome":    nome,
            "role":    role,
            "regioes": regioes,
            "ativo":   True,
        }, on_conflict="email").execute()

        # Dispara convite por email via Supabase Auth
        sb.auth.admin.invite_user_by_email(email)
        return True, None
    except Exception as e:
        return False, str(e)

def rejeitar_solicitacao(sol_id: int) -> tuple:
    try:
        sb = get_supabase()
        sb.table("solicitacoes_acesso").update(
            {"status": "rejeitado"}
        ).eq("id", sol_id).execute()
        return True, None
    except Exception as e:
        return False, str(e)

def listar_usuarios() -> list:
    try:
        sb  = get_supabase()
        res = sb.table("usuarios").select("*").order("nome").execute()
        return res.data or []
    except Exception:
        return []


def listar_bases_disponiveis() -> list:
    """Retorna todas as DS cadastradas no banco (para o admin atribuir)."""
    try:
        sb = get_supabase()
        res = sb.table("expedicao_diaria").select("scan_station").execute()
        if not res.data:
            return []
        return sorted(set(r["scan_station"] for r in res.data))
    except Exception:
        return []

def atualizar_bases_usuario(user_db_id: int, bases: list) -> tuple:
    """Admin atualiza quais bases o usuário pode ver."""
    try:
        sb = get_supabase()
        sb.table("usuarios").update({"bases": bases}).eq("id", user_db_id).execute()
        return True, None
    except Exception as e:
        return False, str(e)


# ══════════════════════════════════════════════════════════════
#  MOTORISTAS STATUS
# ══════════════════════════════════════════════════════════════

def get_motoristas_status() -> dict:
    """Retorna dict {id_motorista: ativo} com todos os motoristas cadastrados."""
    try:
        sb = get_supabase()
        res = sb.table("motoristas_status").select("*").execute()
        return {r["id_motorista"]: r for r in (res.data or [])}
    except Exception:
        return {}

def upsert_motorista_status(id_motorista: str, nome: str, ativo: bool,
                             motivo: str, usuario: str) -> tuple:
    try:
        sb = get_supabase()
        sb.table("motoristas_status").upsert({
            "id_motorista":   id_motorista,
            "nome_motorista": nome,
            "ativo":          ativo,
            "motivo":         motivo,
            "atualizado_em":  "now()",
            "atualizado_por": usuario,
        }, on_conflict="id_motorista").execute()
        return True, None
    except Exception as e:
        return False, str(e)

def listar_motoristas_inativos() -> list:
    """Retorna lista de id_motorista inativos."""
    try:
        sb = get_supabase()
        res = sb.table("motoristas_status").select("id_motorista").eq("ativo", False).execute()
        return [r["id_motorista"] for r in (res.data or [])]
    except Exception:
        return []
