import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createLobby, joinLobby } from '../../api/gameWrapper';

export function HomePage() {
    const navigate = useNavigate();
    const [joinUuid, setJoinUuid] = useState('');

    const handleCreateLobby = async () => {
        try {
            const data = await createLobby();
            navigate('/lobby', { state: { sessionUuid: data.session_uuid } });
        } catch (error) {
            console.error('Error while creating lobby:', error);
        }
    };

    const handleJoinLobby = async () => {
        if (!joinUuid) return;
        
        try {
            await joinLobby(joinUuid);
            navigate('/lobby', { state: { sessionUuid: joinUuid } });
        } catch (error) {
            console.error('Error while joining lobby:', error);
        }
    };

    return (
        <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
            <h1>Quizscendence - Lobby</h1>
            
            <div style={{ marginBottom: '20px', padding: '10px', border: '1px solid black' }}>
                <h2>Create a new game (As Host)</h2>
                <button onClick={handleCreateLobby}>Create Lobby</button>
            </div>

            <div style={{ marginBottom: '20px', padding: '10px', border: '1px solid black' }}>
                <h2>Join an existing game</h2>
                <input 
                    type="text" 
                    placeholder="Enter session UUID" 
                    value={joinUuid} 
                    onChange={(e) => setJoinUuid(e.target.value)} 
                />
                <button onClick={handleJoinLobby}>Join Lobby</button>
            </div>
        </div>
    );
}