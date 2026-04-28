import { useState, useEffect } from 'react'
import { login, logout, register, getUser, initCsrf, connectGameSocket } from './apiWrapper'

enum ApiFeatureName {
  Register = 'register',
  Login = 'login',
  GetUserById = 'getUserById',
  ConnectGameSocket = 'connectGameSocket',
  Logout = 'logout',
}

function App() {
  const [featureName, setFeatureName] = useState('')
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
      case ApiFeatureName.Register:
        const regRes = await register(username, email, password)
        setResult(JSON.stringify(regRes, null, 2))
        break
      case ApiFeatureName.Login:
        const logRes = await login(username, email, password)
        setResult(JSON.stringify(logRes, null, 2))
        break
      case ApiFeatureName.GetUserById:
        const user = await getUser(Number(userId))
        setResult(JSON.stringify(user, null, 2))
        break
      case ApiFeatureName.ConnectGameSocket:
        const gameSocket = connectGameSocket()
        gameSocket.onopen = () => console.log('Game socket opened')
        gameSocket.onmessage = (msg) => console.log('Game socket message:', msg.data)
        gameSocket.onerror = (err) => console.error('Game socket error:', err)
        setResult(JSON.stringify(gameSocket, null, 2))
        break
      case ApiFeatureName.Logout:
        const logoutRes = await logout()
        setResult(JSON.stringify(logoutRes, null, 2))
        break
      default:
        setResult('Please select an action and fill in the required fields.')
        break
    }
  }

  return (
    <div className="App">
      <h1>Quizscendence</h1>
      <select onChange={e => setFeatureName(e.target.value)}>
        <option value={ApiFeatureName.Register}>Register</option>
        <option value={ApiFeatureName.Login}>Login</option>
        <option value={ApiFeatureName.GetUserById}>Get user by id</option>
        <option value={ApiFeatureName.ConnectGameSocket}>Try Game Socket</option>
        <option value={ApiFeatureName.Logout}>Logout</option>
      </select>
      {(featureName === ApiFeatureName.Register || featureName === ApiFeatureName.Login) && (
        <div>
          <input placeholder="username" onChange={e => setUsername(e.target.value)} />
          <input placeholder="password" type="password" onChange={e => setPassword(e.target.value)} />
          <input placeholder="email" type="email" onChange={e => setEmail(e.target.value)} />
        </div>
      )}


      {featureName === ApiFeatureName.GetUserById && (
        <div>
          <input placeholder="user id" onChange={e => setUserId(e.target.value)} />
        </div>
      )}


      {/* we use:  () => func() - to make func work onlcick */}
      <button onClick={() => handleAction(featureName)}>Run</button>
      <pre>{result}</pre>
    </div>

  )
}
export default App
