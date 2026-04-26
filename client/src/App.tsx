import { useState, useEffect } from 'react'
import { login, register, getUser, initCsrf } from './apiWrapper'


function App() {
  const [actionName, setActionName] = useState('')
  //       ^value       ^setter          ^initial value

  const [result, setResult] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [userId, setUserId] = useState('')
  const [email, setEmail] = useState('')

  // Init CSRF cookie for Django once on page load,
  //  required for all POST requests
  //
  //page loads → initCsrf() sets the cookie
  // useEffect runs code after the component renders 
  // The [] at the end means run only once — when the component first appears on the page
  useEffect(() => { initCsrf() }, [])

  async function handleAction(actionName: string) {
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
      default:
        setResult('Please select an action and fill in the required fields.')
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

      {/* we use:  () => func() - to make func work onlcick */}
      <button onClick={() => handleAction(actionName)}>Run</button>
      <pre>{result}</pre>
    </div>

  )
}
export default App
