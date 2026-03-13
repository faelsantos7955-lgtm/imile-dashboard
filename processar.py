"""
processar.py — Script local de processamento iMile Dashboard
============================================================
Roda na máquina do admin. Abre janela visual pra escolher pastas.
As pastas ficam salvas — da próxima vez já lembra onde estavam.

Uso:
    python processar.py        (ou duplo clique no PROCESSAR.bat)

Requisitos:
    pip install supabase pandas openpyxl numpy python-dotenv
    (tkinter já vem com o Python — não precisa instalar)
"""

import os, sys, glob, json, traceback
from datetime import date, datetime, timedelta
from pathlib import Path

SUPABASE_URL = ""
SUPABASE_KEY = ""

CONFIG_FILE = Path(__file__).parent / ".pastas_salvas.json"

SEP  = "=" * 60
SEP2 = "-" * 40

def ok(msg):   print(f"  OK  {msg}")
def err(msg):  print(f"  ERR {msg}")
def info(msg): print(f"  INF {msg}")
def prog(msg): print(f"  ... {msg}")


def _carregar_credenciais():
    global SUPABASE_URL, SUPABASE_KEY
    if SUPABASE_URL and SUPABASE_KEY:
        return
    try:
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent / ".env")
    except ImportError:
        pass
    SUPABASE_URL = SUPABASE_URL or os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = SUPABASE_KEY or os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_KEY", ""))
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\nCredenciais nao encontradas! Verifique o arquivo .env.")
        input("[Enter para sair]")
        sys.exit(1)

def _get_sb():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def _carregar_config():
    try:
        if CONFIG_FILE.exists():
            return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def _salvar_config(cfg):
    try:
        CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:
        pass

def _abrir_janela_pasta(titulo, pasta_inicial=None):
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        pasta = filedialog.askdirectory(
            title=titulo,
            initialdir=pasta_inicial or os.path.expanduser("~\\Downloads")
        )
        root.destroy()
        return pasta or ""
    except Exception:
        return input("  Caminho da pasta: ").strip().strip('"')

def _abrir_janela_arquivo(titulo, pasta_inicial=None):
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        arq = filedialog.askopenfilename(
            title=titulo,
            initialdir=pasta_inicial or os.path.expanduser("~\\Downloads"),
            filetypes=[("Excel", "*.xlsx *.xls"), ("Todos", "*.*")]
        )
        root.destroy()
        return arq or ""
    except Exception:
        return input("  Caminho do arquivo: ").strip().strip('"')

def _escolher_pasta(chave, descricao, cfg, obrigatorio=True):
    pasta_salva = cfg.get(chave, "")
    print(f"\n  >> {descricao}")
    if pasta_salva and os.path.isdir(pasta_salva):
        arquivos = sorted(
            glob.glob(os.path.join(pasta_salva, "*.xlsx")) +
            glob.glob(os.path.join(pasta_salva, "*.xls"))
        )
        print(f"     Pasta salva: {pasta_salva}  ({len(arquivos)} arquivo(s))")
        for a in arquivos:
            print(f"       - {os.path.basename(a)}  ({os.path.getsize(a)/1024/1024:.1f} MB)")
        resp = input("     [Enter] usar  |  [t] trocar  |  [p] pular: ").strip().lower()
        if resp == "p":
            return [] if not obrigatorio else _escolher_pasta(chave, descricao, cfg, obrigatorio)
        if resp != "t" and arquivos:
            return arquivos

    print("     Abrindo seletor de pasta...")
    nova = _abrir_janela_pasta(f"Selecionar pasta -- {descricao}", pasta_salva)
    if not nova:
        return [] if not obrigatorio else []
    arquivos = sorted(
        glob.glob(os.path.join(nova, "*.xlsx")) +
        glob.glob(os.path.join(nova, "*.xls"))
    )
    if not arquivos:
        print(f"     Nenhum arquivo Excel em: {nova}")
        return []
    cfg[chave] = nova
    _salvar_config(cfg)
    for a in arquivos:
        print(f"       - {os.path.basename(a)}  ({os.path.getsize(a)/1024/1024:.1f} MB)")
    return arquivos

def _escolher_arquivo(chave, descricao, cfg, obrigatorio=True):
    arq_salvo = cfg.get(chave, "")
    print(f"\n  >> {descricao}")
    if arq_salvo and os.path.isfile(arq_salvo):
        print(f"     Arquivo salvo: {os.path.basename(arq_salvo)}  ({os.path.getsize(arq_salvo)/1024/1024:.1f} MB)")
        resp = input("     [Enter] usar  |  [t] trocar  |  [p] pular: ").strip().lower()
        if resp == "p":
            return ""
        if resp != "t":
            return arq_salvo
    print("     Abrindo seletor de arquivo...")
    novo = _abrir_janela_arquivo(
        f"Selecionar -- {descricao}",
        os.path.dirname(arq_salvo) if arq_salvo else None
    )
    if not novo:
        return ""
    cfg[chave] = novo
    _salvar_config(cfg)
    print(f"       - {os.path.basename(novo)}  ({os.path.getsize(novo)/1024/1024:.1f} MB)")
    return novo

def _pedir_data(default=None):
    if default is None:
        default = date.today() - timedelta(days=1)
    while True:
        entrada = input(f"\n  Data (dd/mm/aaaa) [{default.strftime('%d/%m/%Y')}]: ").strip()
        if not entrada:
            return default
        try:
            return datetime.strptime(entrada, "%d/%m/%Y").date()
        except ValueError:
            print("     Formato invalido. Use dd/mm/aaaa.")


def processar_dashboard():
    print(f"\n{SEP}\n  DASHBOARD\n{SEP}")
    cfg = _carregar_config()
    arqs_rec = _escolher_pasta("dash_recebimento",  "Recebimento",          cfg)
    arqs_out = _escolher_pasta("dash_out_delivery", "Out of Delivery",      cfg)
    arqs_ent = _escolher_pasta("dash_entregas",     "Entregas / Delivered", cfg, obrigatorio=False)
    arq_sup  = _escolher_arquivo("dash_supervisores", "Supervisores (SIGLA, REGION) -- pule se ja no banco", cfg, obrigatorio=False)
    arq_meta = _escolher_arquivo("dash_metas",        "Metas por Base -- pule se ja no banco",              cfg, obrigatorio=False)

    if not arqs_rec or not arqs_out:
        err("Recebimento e Out of Delivery sao obrigatorios.")
        return

    data_ref = _pedir_data()
    print(f"\n  Processando: {data_ref.strftime('%d/%m/%Y')}\n{SEP2}")

    import pandas as pd, numpy as np, re

    _ENGINE = "openpyxl"
    try:
        import python_calamine
        _ENGINE = "calamine"
    except ImportError:
        pass

    try:
        def _ler(arqs, cols):
            frames = []
            for a in arqs:
                try:
                    df = pd.read_excel(a, engine=_ENGINE, usecols=lambda c: c in cols)
                except Exception:
                    df = pd.read_excel(a, engine=_ENGINE)
                frames.append(df)
            return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

        def _lc(s):
            return s.astype(str).str.strip().str.upper().str.replace(r'\s+', ' ', regex=True)

        def _wb(s):
            try:
                return s.astype(float).astype('int64').astype(str).str.strip()
            except Exception:
                return s.astype(str).str.strip()

        sb = _get_sb()

        prog("Carregando supervisores...")
        if arq_sup:
            ds = pd.read_excel(arq_sup, engine=_ENGINE)
            ds.columns = [c.strip().upper() for c in ds.columns]
            ds["SIGLA"] = _lc(ds["SIGLA"])
            sb.table("config_supervisores").upsert(
                [
                    {
                        "sigla": str(r["SIGLA"]),
                        "region": str(r["REGION"]).strip(),
                        "atualizado_por": "processar.py"
                    }
                    for _, r in ds.iterrows() if str(r["SIGLA"]).strip()
                ],
                on_conflict="sigla"
            ).execute()
            ok(f"{len(ds)} supervisores salvos.")
            df_sup = ds
        else:
            res = sb.table("config_supervisores").select("sigla,region").execute()
            if not res.data:
                err("Sem supervisores no banco.")
                return
            df_sup = pd.DataFrame(res.data)
            df_sup.columns = ["SIGLA", "REGION"]
            df_sup["SIGLA"] = _lc(df_sup["SIGLA"])
            info(f"{len(df_sup)} supervisores do banco.")

        prog("Carregando recebimento...")
        df_rec = _ler(arqs_rec, {"Scan Station", "Waybill Number", "Destination City"})
        dcol = next((c for c in df_rec.columns if any(k in c.lower() for k in ["scan time", "data", "date", "inbound"])), None)
        if dcol:
            df_rec[dcol] = pd.to_datetime(df_rec[dcol], errors="coerce")
            antes = len(df_rec)
            df_rec = df_rec[df_rec[dcol].dt.date == data_ref].copy()
            ok(f"Recebimento: {len(df_rec):,} de {antes:,} registros")
        else:
            info(f"Recebimento: {len(df_rec):,} registros (sem filtro de data)")

        prog("Carregando out of delivery...")
        df_out = _ler(arqs_out, {"Waybill No.", "Scan time"})
        ok(f"Out of delivery: {len(df_out):,}")

        df_ent = None
        if arqs_ent:
            prog("Carregando entregas...")
            df_ent = _ler(arqs_ent, {"Scan Station", "Waybill No."})
            ok(f"Entregas: {len(df_ent):,}")

        df_meta = None
        if arq_meta:
            dm = pd.read_excel(arq_meta, engine=_ENGINE)
            dm.columns = [c.strip().upper() for c in dm.columns]
            cd = next((c for c in dm.columns if "DS" in c or "BASE" in c), None)
            cm = next((c for c in dm.columns if "META" in c), None)
            if cd and cm:
                dm = dm.rename(columns={cd: "DS", cm: "Meta"})
                mn = pd.to_numeric(
                    dm["Meta"].astype(str).str.replace("%", "", regex=False).str.replace(",", ".", regex=False),
                    errors="coerce"
                )
                mn = mn.where(mn <= 1.0, mn / 100)
                dm["Meta"] = mn.fillna(0.5)
                df_meta = dm[["DS", "Meta"]]
                sb.table("config_metas").upsert(
                    [
                        {"ds": r["DS"], "meta": float(r["Meta"]), "atualizado_por": "processar.py"}
                        for _, r in df_meta.iterrows() if r["DS"]
                    ],
                    on_conflict="ds"
                ).execute()
                ok(f"{len(df_meta)} metas salvas.")

        if df_meta is None:
            rm = sb.table("config_metas").select("ds,meta").execute()
            if rm.data:
                df_meta = pd.DataFrame(rm.data)
                df_meta.columns = ["DS", "Meta"]
                info(f"{len(df_meta)} metas do banco.")

        prog("Calculando...")
        mapa = {}
        for _, row in df_sup.iterrows():
            sig, reg = row["SIGLA"], row["REGION"]
            mapa[sig] = (sig, reg)
            cod = re.sub(r'^(RDC|DC|DS)[\s\-]+', '', sig).strip()
            if cod not in mapa:
                mapa[cod] = (sig, reg)

        def _pad(df, col="Scan Station"):
            df = df.copy()
            df[col] = _lc(df[col])
            ms = {k: v[0] for k, v in mapa.items()}
            m = df[col].map(ms)
            sem = m.isna()
            if sem.any():
                cod = df.loc[sem, col].str.replace(r'^(RDC|DC|DS)[\s\-]+', '', regex=True).str.strip()
                m[sem] = cod.map(ms)
            df[col] = m.fillna(df[col])
            return df

        if "Scan Station" in df_rec.columns:
            df_rec["Scan Station"] = _lc(df_rec["Scan Station"])
            ms = {k: v[0] for k, v in mapa.items()}
            mr = {k: v[1] for k, v in mapa.items()}
            m = df_rec["Scan Station"].map(ms)
            sem = m.isna()
            if sem.any():
                cod = df_rec.loc[sem, "Scan Station"].str.replace(r'^(RDC|DC|DS)[\s\-]+', '', regex=True).str.strip()
                m[sem] = cod.map(ms)
            df_rec["Scan Station"] = m.fillna(df_rec["Scan Station"])
            df_rec["REGION"] = df_rec["Scan Station"].map(mr).fillna("Sem Classificacao")

        if "Scan Station" not in df_out.columns and "Waybill No." in df_out.columns:
            wss = df_rec[["Waybill Number", "Scan Station"]].dropna().drop_duplicates("Waybill Number").rename(columns={"Waybill Number": "Waybill No."})
            df_out = df_out.merge(wss, on="Waybill No.", how="left")
        elif "Scan Station" in df_out.columns:
            df_out = _pad(df_out)

        if df_ent is not None and "Scan Station" in df_ent.columns:
            df_ent = _pad(df_ent)

        ds_base = df_rec[["Scan Station", "REGION"]].drop_duplicates("Scan Station").dropna(subset=["Scan Station"])
        dw = df_rec.dropna(subset=["Waybill Number"]).copy() if "Waybill Number" in df_rec.columns else df_rec.copy()

        if "Waybill Number" in dw.columns:
            dw["Waybill Number"] = _wb(dw["Waybill Number"])
            dw = dw.drop_duplicates("Waybill Number")
            rec = dw.groupby("Scan Station").size().reset_index(name="Recebido")
            wb_set = set(dw["Waybill Number"])
        else:
            rec = df_rec["Scan Station"].value_counts().reset_index(name="Recebido")
            wb_set = set()

        if "Waybill No." in df_out.columns and "Scan Station" in df_out.columns and wb_set:
            df_out["Waybill No."] = _wb(df_out["Waybill No."])
            do2 = df_out[df_out["Waybill No."].isin(wb_set)].drop_duplicates("Waybill No.")
            exp = do2.groupby("Scan Station").size().reset_index(name="Expedido")
        elif "Scan Station" in df_out.columns:
            exp = df_out["Scan Station"].value_counts().reset_index(name="Expedido")
        else:
            exp = pd.DataFrame(columns=["Scan Station", "Expedido"])

        p = ds_base.merge(rec, on="Scan Station", how="left").merge(exp, on="Scan Station", how="left")
        p["Recebido"] = p["Recebido"].fillna(0).astype(int)
        p["Expedido"] = p["Expedido"].fillna(0).astype(int)

        if df_ent is not None and "Waybill No." in df_ent.columns and wb_set:
            df_ent["Waybill No."] = _wb(df_ent["Waybill No."])
            de2 = df_ent[df_ent["Waybill No."].isin(wb_set)].drop_duplicates("Waybill No.")
            ent = de2.groupby("Scan Station").size().reset_index(name="Entregas")
            p["Entregas"] = p["Scan Station"].map(ent.set_index("Scan Station")["Entregas"]).fillna(0).astype(int)
        else:
            p["Entregas"] = 0

        p["taxa_exp"] = np.where(p["Recebido"] > 0, p["Expedido"] / p["Recebido"], 0.0)
        p["taxa_ent"] = np.where(p["Recebido"] > 0, (p["Entregas"] / p["Recebido"]).clip(upper=1.0), 0.0)
        p["meta"] = p["Scan Station"].map(df_meta.set_index("DS")["Meta"].to_dict()).fillna(0.5) if df_meta is not None else 0.5
        p["atingiu_meta"] = p["taxa_exp"] >= p["meta"]

        prog("Salvando no Supabase...")
        rows_d = [
            {
                "data_ref": str(data_ref),
                "scan_station": str(r["Scan Station"]),
                "region": str(r.get("REGION", "")),
                "recebido": int(r["Recebido"]),
                "expedido": int(r["Expedido"]),
                "entregas": int(r["Entregas"]),
                "taxa_exp": float(r["taxa_exp"]),
                "taxa_ent": float(r["taxa_ent"]),
                "meta": float(r["meta"]),
                "atingiu_meta": bool(r["atingiu_meta"]),
                "processado_por": "processar.py"
            }
            for _, r in p.iterrows()
        ]
        if rows_d:
            sb.table("expedicao_diaria").upsert(rows_d, on_conflict="data_ref,scan_station").execute()
            ok(f"{len(rows_d)} stations salvas.")

        rec_t = int(p["Recebido"].sum())
        exp_t = int(p["Expedido"].sum())
        ent_t = int(p["Entregas"].sum())
        n_ok = int(p["atingiu_meta"].sum())

        print(f"\n{SEP}\n  DASHBOARD PROCESSADO!\n{SEP}")
        print(f"  Data: {data_ref.strftime('%d/%m/%Y')}  |  Recebido: {rec_t:,}  |  Expedido: {exp_t:,}  |  Entregas: {ent_t:,}  |  Meta: {n_ok}/{len(p)}")
        print(SEP)
    except Exception:
        err("ERRO:")
        print(traceback.format_exc())


def processar_reclamacoes():
    print(f"\n{SEP}\n  RECLAMACOES\n{SEP}")
    cfg = _carregar_config()

    arq_bilhete   = _escolher_arquivo("rec_bilhete",   "Bilhete de Reclamacao",             cfg)
    arq_carta     = _escolher_arquivo("rec_carta",     "Consulta a Carta de Porte Central", cfg)
    arq_gestao    = _escolher_arquivo("rec_gestao",    "Gestao de Bases (Supervisores)",    cfg, obrigatorio=False)
    arq_delivered = _escolher_arquivo("rec_delivered", "Delivered / Entregas",               cfg, obrigatorio=False)

    if not arq_bilhete or not arq_carta:
        err("Bilhete e Carta de Porte sao obrigatorios.")
        return

    print(f"\n{SEP2}")

    import pandas as pd, io as _io

    _ENGINE = "openpyxl"
    try:
        import python_calamine
        _ENGINE = "calamine"
    except ImportError:
        pass

    try:
        _proj = Path(__file__).parent
        if str(_proj) not in sys.path:
            sys.path.insert(0, str(_proj))

        from modulos.reclamacoes import (
            carregar_bilhete,
            adicionar_supervisor,
            criar_colunas_auxiliares,
            cruzar_carta_porte,
            limpar_dados,
            separar_periodo,
            agregar_por_supervisor,
            agregar_por_station,
            top5_motoristas,
            carregar_delivered,
            gerar_excel
        )

        sb = _get_sb()

        res_i = sb.table("motoristas_status").select("id_motorista").eq("ativo", False).execute()
        inativos = [r["id_motorista"] for r in (res_i.data or [])]

        prog("Carregando bilhete...")
        df = carregar_bilhete(arq_bilhete)
        ok(f"{len(df):,} registros.")

        prog("Supervisores...")
        if arq_gestao:
            df = adicionar_supervisor(df, open(arq_gestao, "rb"))
        else:
            rs = sb.table("config_supervisores").select("sigla,region").execute()
            buf = _io.BytesIO()
            pd.DataFrame(rs.data).rename(columns={"sigla": "SIGLA", "region": "SUPERVISOR"}).to_excel(buf, index=False)
            buf.seek(0)
            df = adicionar_supervisor(df, buf)

        df = criar_colunas_auxiliares(df)

        prog("Carta de porte...")
        df = cruzar_carta_porte(df, open(arq_carta, "rb"))

        df = limpar_dados(df)
        df_dia, df_mes, data_ref = separar_periodo(df)

        prog("Agregando...")
        agg_sup = agregar_por_supervisor(df_dia, df_mes)
        agg_sta = agregar_por_station(df_dia, df_mes)
        top5 = top5_motoristas(df_dia, inativos=inativos)

        est = pd.DataFrame(columns=["Delivery Station", "Total Entregas"])
        esup = pd.DataFrame(columns=["Supervisor", "Total Entregas"])
        df_del_raw = None

        if arq_delivered:
            g2 = open(arq_gestao, "rb") if arq_gestao else _io.BytesIO()
            est, esup = carregar_delivered(open(arq_delivered, "rb"), g2)
            df_del_raw = pd.read_excel(arq_delivered, engine=_ENGINE, dtype=str)

        prog("Salvando...")

        up = sb.table("reclamacoes_uploads").insert({
            "data_ref": data_ref.isoformat(),
            "n_registros": len(df),
            "n_sup": int(agg_sup["Supervisor"].nunique()),
            "n_sta": int(agg_sta["Inventory Station"].nunique()),
            "n_mot": int(df["Motorista"].notna().sum())
        }).execute()
        print("PASSOU INSERT UPLOAD")
        print(up)

        uid = up.data[0]["id"]

        if not agg_sup.empty:
            sb.table("reclamacoes_por_supervisor").insert([
                {
                    "upload_id": uid,
                    "supervisor": str(r["Supervisor"]),
                    "dia_total": int(r.iloc[1]),
                    "mes_total": int(r.iloc[2])
                }
                for _, r in agg_sup.iterrows()
            ]).execute()
        print("PASSOU SUPERVISOR")

        if not agg_sta.empty:
            sb.table("reclamacoes_por_station").insert([
                {
                    "upload_id": uid,
                    "station": str(r["Inventory Station"]),
                    "dia_total": int(r.iloc[1]),
                    "mes_total": int(r.iloc[2])
                }
                for _, r in agg_sta.iterrows()
            ]).execute()
        print("PASSOU STATION")

        if not top5.empty:
            sb.table("reclamacoes_top5").insert([
                {
                    "upload_id": uid,
                    "motorista": str(r.iloc[0]),
                    "total": int(r.iloc[2] if len(r) > 2 else r.iloc[1])
                }
                for _, r in top5.iterrows()
            ]).execute()
        print("PASSOU TOP5")

        ok(f"Salvo (id={uid}).")

        prog("Gerando Excel...")
        print("ANTES DO GERAR_EXCEL")
        excel = gerar_excel(df, agg_sup, agg_sta, top5, est, esup, data_ref, df_del_raw)
        print("DEPOIS DO GERAR_EXCEL")

        nome = f"reclamacoes_{data_ref.strftime('%Y%m%d')}.xlsx"
        print("ANTES DE GRAVAR ARQUIVO")
        Path(nome).write_bytes(excel)
        print("DEPOIS DE GRAVAR ARQUIVO")

        ok(f"Excel: {nome}")

        print(f"\n{SEP}\n  RECLAMACOES PROCESSADAS!\n{SEP}\n  Data: {data_ref.strftime('%d/%m/%Y')}  |  Registros: {len(df):,}\n{SEP}")

    except Exception:
        err("ERRO:")
        print(traceback.format_exc())


def processar_triagem():
    print(f"\n{SEP}\n  TRIAGEM DC x DS\n{SEP}")
    cfg = _carregar_config()
    arqs_scans = _escolher_pasta("tri_scans", "Loading Scan(s)", cfg)
    arq_bases  = _escolher_arquivo("tri_bases", "Arquivo Bases (BASE, BASE_PAI, SUPERVISOR)", cfg)

    if not arqs_scans or not arq_bases:
        err("Loading Scans e Arquivo Bases sao obrigatorios.")
        return

    print(f"\n{SEP2}")

    try:
        _proj = Path(__file__).parent
        if str(_proj) not in sys.path:
            sys.path.insert(0, str(_proj))

        from modulos.triagem import run_analysis
        import io as _io

        def log_cb(msg):
            print(f"     {msg}")

        def prog_cb(v):
            pass

        scans = []
        for a in arqs_scans:
            buf = _io.BytesIO(Path(a).read_bytes())
            buf.name = os.path.basename(a)
            scans.append(buf)

        bb = _io.BytesIO(Path(arq_bases).read_bytes())
        bb.name = os.path.basename(arq_bases)

        ok_flag, res, err_msg = run_analysis(scans, bb, log_cb, prog_cb)
        if not ok_flag:
            err(f"Analise falhou: {err_msg}")
            return

        prog("Salvando...")
        sb = _get_sb()

        up = sb.table("triagem_uploads").insert({
            "data_ref": date.today().isoformat(),
            "criado_por": "processar.py",
            "total": int(res["total"]),
            "qtd_ok": int(res["ok"]),
            "qtd_erro": int(res["erro"]),
            "qtd_fora": int(res["fora"]),
            "taxa": float(res["taxa"])
        }).execute()

        uid = up.data[0]["id"]

        if not res["r_dc"].empty:
            sb.table("triagem_por_ds").insert([
                {
                    "upload_id": uid,
                    "ds": str(r.iloc[0]),
                    "total": int(r["Total Expedido"]),
                    "ok": int(r["Triagem OK"]),
                    "nok": int(r["Triagem NOK"]),
                    "fora": int(r["Fora Abrangencia"]),
                    "taxa": float(r["Taxa (%)"])
                }
                for _, r in res["r_dc"].iterrows()
            ]).execute()

        if not res["top5"].empty:
            sb.table("triagem_top5").insert([
                {
                    "upload_id": uid,
                    "ds": str(r["DS"]),
                    "total_erros": int(r["Total Erros"])
                }
                for _, r in res["top5"].iterrows()
            ]).execute()

        if not res["r_sup"].empty:
            sb.table("triagem_por_supervisor").insert([
                {
                    "upload_id": uid,
                    "supervisor": str(r.iloc[0]),
                    "total": int(r["Total Expedido"]),
                    "ok": int(r["Triagem OK"]),
                    "nok": int(r["Triagem NOK"]),
                    "fora": int(r["Fora Abrangencia"]),
                    "taxa": float(r["Taxa (%)"])
                }
                for _, r in res["r_sup"].iterrows()
            ]).execute()

        ok(f"Salvo (id={uid}).")

        nome = f"Relatorio_Triagem_{date.today().strftime('%Y%m%d')}.xlsx"
        Path(nome).write_bytes(res["excel_bytes"])
        ok(f"Excel: {nome}")

        print(f"\n{SEP}\n  TRIAGEM PROCESSADA!\n{SEP}\n  Total: {res['total']:,}  |  OK: {res['ok']:,}  |  Erro: {res['erro']:,}  |  Taxa: {res['taxa']:.1f}%\n{SEP}")

    except Exception:
        err("ERRO:")
        print(traceback.format_exc())


MODULOS = {
    "1": ("Dashboard",   processar_dashboard),
    "2": ("Reclamacoes", processar_reclamacoes),
    "3": ("Triagem",     processar_triagem),
}

def main():
    _carregar_credenciais()
    while True:
        print(f"\n{SEP}\n  iMile -- PROCESSADOR LOCAL\n{SEP}")
        for k, (nome, _) in MODULOS.items():
            print(f"    [{k}]  {nome}")
        print("    [0]  Sair\n")
        escolha = input("  Opcao: ").strip()
        if escolha == "0":
            print("  Ate mais!\n")
            break
        if escolha in MODULOS:
            _, fn = MODULOS[escolha]
            fn()
            input("\n  [Enter] para voltar ao menu...")
        else:
            print("  Opcao invalida.")

if __name__ == "__main__":
    main()