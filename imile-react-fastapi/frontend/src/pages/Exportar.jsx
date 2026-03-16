import { Link } from "react-router-dom"

export default function Exportar() {
  return (
    <div style={{ padding: 30 }}>
      <Link to="/dashboard">← Voltar</Link>
      <h1>Exportar</h1>
      <p>Página de exportação de relatórios.</p>
    </div>
  )
}