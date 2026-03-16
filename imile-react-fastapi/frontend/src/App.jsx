import { useState } from "react"

function App() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [result, setResult] = useState(null)

  const login = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      })

      const data = await res.json()

      if (data.access_token) {
        localStorage.setItem("token", data.access_token)
        window.location.href = "/dashboard"
        return
      }

      setResult(data)
    } catch (err) {
      setResult({ error: String(err) })
    }
  }

  return (
    <div style={{ padding: 40, color: "black" }}>
      <h1>iMile Portal</h1>

      <input
        placeholder="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />

      <br />
      <br />

      <input
        type="password"
        placeholder="senha"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />

      <br />
      <br />

      <button onClick={login}>Login</button>

      <pre>{JSON.stringify(result, null, 2)}</pre>
    </div>
  )
}

export default App