import { useEffect, useState } from 'react'

const API = '/api/mobile/'

async function request(path, token, options = {}) {
  const response = await fetch(API + path, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}), Authorization: `Token ${token}` }
  })
  let data = {}
  try { data = await response.json() } catch {}
  return [response, data]
}

const screens = [
  ['home', '🏠 Menu'], ['consulta', '🔎 Consulta'], ['recebimento', '📥 Recebimento'],
  ['armazenagem', '📦 Armazenagem'], ['inventario', '📋 Inventário'],
  ['separacao', '🛒 Separação'], ['imei', '📱 IMEI']
]

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('wms_token') || '')
  const [user, setUser] = useState('')
  const [screen, setScreen] = useState('home')
  const [login, setLogin] = useState({ username: '', password: '' })
  const [message, setMessage] = useState('')
  const [code, setCode] = useState('')
  const [result, setResult] = useState('')

  useEffect(() => {
    if (!token) return
    request('me/', token).then(([r, d]) => {
      if (r.ok) setUser(d.user || '')
      else { localStorage.removeItem('wms_token'); setToken('') }
    })
  }, [token])

  async function doLogin() {
    const r = await fetch(API + 'login/', {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(login)
    })
    const d = await r.json()
    if (!r.ok) return setMessage(d.error || 'Login inválido')
    localStorage.setItem('wms_token', d.token); setToken(d.token); setMessage('')
  }

  async function lookup(value = code) {
    const valueTrimmed = String(value).trim()
    if (!valueTrimmed) return
    const [r, d] = await request(`scan/?code=${encodeURIComponent(valueTrimmed)}`, token)
    if (!r.ok) return setResult(d.error || 'Erro na consulta')
    const stock = (d.stock || []).map(s => `📍 ${s.address} — disponível ${s.available} — total ${s.quantity}`).join('\n')
    setResult(`${d.product.description}\n${d.product.code}\n\n${stock || 'Sem estoque'}`)
  }

  function logout() { localStorage.removeItem('wms_token'); setToken(''); setUser('') }

  if (!token) return <div className="wrap"><div className="card"><h2>Login</h2><input placeholder="Usuário" value={login.username} onChange={e => setLogin({ ...login, username: e.target.value })}/><input type="password" placeholder="Senha" value={login.password} onChange={e => setLogin({ ...login, password: e.target.value })}/><button onClick={doLogin}>ENTRAR</button>{message && <div className="result error">{message}</div>}</div></div>

  return <>
    <header><b>📦 WMS Mobile</b><span>{user}</span></header>
    <div className="wrap">
      <div className="card nav">{screens.map(([id, label]) => <button key={id} onClick={() => setScreen(id)}>{label}</button>)}<button className="secondary" onClick={logout}>SAIR</button></div>
      {screen === 'home' && <div className="card"><h2>Operação móvel</h2><p>Use a câmera para produtos, endereços, QR Codes, EAN e IMEI.</p><div className="result ok">Pronto para operar.</div></div>}
      {screen === 'consulta' && <div className="card"><h2>Consulta de estoque</h2><input placeholder="EAN / QR / código" value={code} onChange={e => setCode(e.target.value)}/><button onClick={() => lookup()}>CONSULTAR</button><pre className="result">{result}</pre></div>}
      {screen !== 'home' && screen !== 'consulta' && <div className="card"><h2>{screens.find(x => x[0] === screen)?.[1]}</h2><div className="result">Tela React preparada. As funções atuais continuam no coletor original.</div></div>}
    </div>
  </>
}
