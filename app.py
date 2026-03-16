import { useState } from "react"

function App() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const login = async () => {
    try {
      setLoading(true)
      setResult(null)

      const res = await fetch("http://127.0.0.1:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      })

      const data = await res.json()
      setResult({
        status: res.status,
        ok: res.ok,
        data,
      })
    } catch (err) {
      setResult({
        error: String(err),
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ padding: 40 }}>
      <h1>iMile Portal</h1>

      <input
        placeholder="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <br /><br />

      <input
        type="password"
        placeholder="senha"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <br /><br />

      <button onClick={login} disabled={loading}>
        {loading ? "Entrando..." : "Login"}
      </button>

      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  )
}

export default App