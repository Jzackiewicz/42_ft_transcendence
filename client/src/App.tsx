import { useState, useEffect } from 'react'
import { login, register, getUser, initCsrf } from './api'


function App() {
  const [actionName, setActionName] = useState('')
  const [result, setResult] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [userId, setUserId] = useState('')
  const [email, setEmail] = useState('')

  useEffect(() => { initCsrf() }, [])

  async function handleAction(actionName: string) {
    // setResult()
    console.log(`Action run: ${actionName}`)

    switch (actionName) {
      case 'register':
        const regRes = await register(username, email, password)
        setResult(JSON.stringify(regRes, null, 2))
        break
      case 'login':
        const logRes = await login(username, email, password)
        setResult(JSON.stringify(logRes, null, 2))
        break
      case 'getUserById':
        const user = await getUser(Number(userId))
        setResult(JSON.stringify(user, null, 2))
        break
    }
  }

  return (
  <div className="App">
    <h1>Quizscendence</h1>
    <select onChange={e => setActionName(e.target.value)}>
      <option value="">-- select action --</option>
      <option value="register">Register</option>
      <option value="login">Login</option>
      <option value="getUserById">Get user by id</option>
    </select>
    {(actionName === 'login' || actionName === 'register') && (
    <div>
      <input placeholder="username" onChange={e => setUsername(e.target.value)} />
      <input placeholder="password" type="password" onChange={e => setPassword(e.target.value)} />
      <input placeholder="email" type="email" onChange={e => setEmail(e.target.value)} />
    </div>
  )}

  {actionName === 'getUserById' && (
    <div>
      <input placeholder="user id" onChange={e => setUserId(e.target.value)} />
    </div>
  )}

    <button onClick={() => handleAction(actionName)}>Run</button>
    <pre>{result}</pre>
  </div>
  
)
}
export default App
