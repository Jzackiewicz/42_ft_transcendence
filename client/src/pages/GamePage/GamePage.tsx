import { useGamePage } from './useGamePage';

export function GamePage() {
    // Extract variables and functions from the custom hook
    const { sessionUuid, messages, isConnected, disconnect } = useGamePage();

    return (
        <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
            <h1>Game Room</h1>
            <p><strong>Session UUID:</strong> {sessionUuid || 'None'}</p>
            <p>
                <strong>Connection Status: </strong> 
                <span style={{ color: isConnected ? 'green' : 'red' }}>
                    {isConnected ? 'Connected (WebSocket Online)' : 'Disconnected'}
                </span>
            </p>

            <div style={{ marginTop: '20px', border: '1px solid #ccc', padding: '10px', height: '300px', overflowY: 'scroll' }}>
                <h3>Server Logs (WS Messages):</h3>
                <ul>
                    {messages.map((msg, index) => (
                        <li key={index}>{msg}</li>
                    ))}
                </ul>
            </div>

            <br />
            <button onClick={disconnect}>Force Disconnect</button>
        </div>
    );
}