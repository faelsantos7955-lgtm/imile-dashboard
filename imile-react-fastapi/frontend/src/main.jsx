import React from "react"
import ReactDOM from "react-dom/client"
import { BrowserRouter, Routes, Route } from "react-router-dom"
import App from "./App.jsx"
import Dashboard from "./pages/Dashboard.jsx"
import Reclamacoes from "./pages/Reclamacoes.jsx"
import Triagem from "./pages/Triagem.jsx"
import Graficos from "./pages/Graficos.jsx"
import Exportar from "./pages/Exportar.jsx"
import "./index.css"

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/reclamacoes" element={<Reclamacoes />} />
        <Route path="/triagem" element={<Triagem />} />
        <Route path="/graficos" element={<Graficos />} />
        <Route path="/exportar" element={<Exportar />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)