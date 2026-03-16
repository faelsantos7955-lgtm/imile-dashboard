import { Link } from "react-router-dom"

export default function Graficos() {
  return (
    <div style={{ padding: 30 }}>
      <Link to="/dashboard">← Voltar</Link>
      <h1>Gráficos</h1>
      <p>Página de gráficos operacionais.</p>
    </div>
  )
}