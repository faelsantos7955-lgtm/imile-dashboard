# iMile Dashboard — React + FastAPI

Portal operacional de logística com frontend React e backend FastAPI.

## Estrutura

```
imile-react/
├── backend/                  # API Python (FastAPI)
│   ├── api/
│   │   ├── main.py          # Entry point
│   │   ├── deps.py          # Supabase client + auth
│   │   └── routes/
│   │       ├── auth.py      # Login, registro
│   │       ├── dashboard.py # KPIs, charts
│   │       ├── historico.py # Período
│   │       ├── reclamacoes.py
│   │       ├── triagem.py
│   │       └── admin.py     # Usuários, motoristas
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                 # React + Vite + Tailwind
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.jsx   # Sidebar + content area
│   │   │   └── ui.jsx       # KpiCard, RankingRow, etc
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Historico.jsx
│   │   │   ├── Triagem.jsx
│   │   │   ├── Reclamacoes.jsx
│   │   │   └── Admin.jsx
│   │   ├── lib/
│   │   │   ├── api.js       # Axios client
│   │   │   └── AuthContext.jsx
│   │   ├── App.jsx          # Router
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
```

## Setup — Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Criar .env com credenciais do Supabase
cp .env.example .env
# Editar .env com suas chaves

# Rodar
uvicorn api.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Setup — Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

O Vite faz proxy automático de `/api/*` para `localhost:8000`.

## Deploy — Produção

### Backend → Railway / Render
- Configurar variáveis de ambiente (SUPABASE_URL, etc.)
- Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### Frontend → Vercel
- Build: `npm run build`
- Env var: `VITE_API_URL=https://seu-backend.railway.app`
