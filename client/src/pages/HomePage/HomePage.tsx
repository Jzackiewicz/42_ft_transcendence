import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createLobby, joinLobby } from '../../api/gameWrapper';
import { logout } from '../../api/authWrapper';
import { useUser } from '../../context/UserContext';

export function HomePage() {
    const navigate = useNavigate();
    const { setUser } = useUser();
    const [joinUuid, setJoinUuid] = useState('');
    const [showJoinModal, setShowJoinModal] = useState(false);

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
            setShowJoinModal(false);
            navigate('/lobby', { state: { sessionUuid: joinUuid } });
        } catch (error) {
            console.error('Error while joining lobby:', error);
        }
    };

    const handleLogout = async () => {
        try {
            await logout();
            setUser(null);
            navigate('/login');
        } catch (error) {
            console.error('Error while logging out:', error);
        }
    };

    return (
        <div>
            <h1>Home page</h1>
            
            <button onClick={() => setShowJoinModal(true)}>
                Join lobby
            </button>
            
            <button onClick={handleCreateLobby}>
                Create Lobby
            </button>
            
            <button onClick={handleLogout}>
                Logout
            </button>

            {showJoinModal && (
                <div style={{
                    position: 'fixed',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    backgroundColor: 'transparent',
                    border: '2px solid white',
                    padding: '20px',
                    zIndex: 1000
                }}>
                    <h3>Join Lobby</h3>
                    <input 
                        type="text" 
                        placeholder="Lobby UUID" 
                        value={joinUuid} 
                        onChange={(e) => setJoinUuid(e.target.value)} 
                    />
                    <br /><br />
                    <button onClick={handleJoinLobby}>Join</button>
                    <button onClick={() => setShowJoinModal(false)}>Cancel</button>
                </div>
            )}
        </div>
    );
}