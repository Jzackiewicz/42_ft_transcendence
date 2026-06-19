import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv'
import AccountHeader from './SubviewsHomePage/AccountHeader/AccountHeader'
import FriendsView from './SubviewsHomePage/FriendsView/FriendsView'
import ChatContainer from './SubviewsHomePage/ChatContainer/ChatContainer'
import SolarSystem from './SubviewsHomePage/Solar/SolarSystem'
import { Navbar } from '../../components/Navbar/Navbar'

import './HomePage.css'

import { useHomePage } from './useHomePage'
import { FriendsProvider } from '../../context/FriendsListContext'

export function HomePage() {
    const {
        user,
        handleLogout,
        handleCreateLobby,
        handleJoinLobby,
        joinUuid, setJoinUuid,
        showJoinModal, setShowJoinModal,
    } = useHomePage()

    return (
        <FriendsProvider>
        <div className="home-page-container">
            <BlinkingSpaceBGDiv />

            {/* ── Nav ── */}
            <Navbar 
                actionButtonText="Logout"
                onActionButtonClick={handleLogout}
            />

            {/* ── Join modal ── */}
            {showJoinModal && (
                <div className="join-modal-overlay">
                    <div className="join-modal">
                        <h3 className="join-modal-title">Join Lobby</h3>
                        <input
                            className="join-modal-input"
                            type="text"
                            placeholder="Paste lobby UUID…"
                            value={joinUuid}
                            onChange={e => setJoinUuid(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleJoinLobby()}
                        />
                        <div className="join-modal-actions">
                            <button className="home-nav-play" onClick={handleJoinLobby}>Join</button>
                            <button className="join-modal-cancel" onClick={() => setShowJoinModal(false)}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}

            {/* ── Main ── */}
            <main className="home-content">
                <AccountHeader
                    username={user?.username ?? ''}
                    email={user?.email ?? ''}
                    setShowJoinModal={setShowJoinModal}
                    handleCreateLobby={handleCreateLobby}
                />

                <div className="account-grid">
                    <FriendsView />
                    <SolarSystem />

                    <div className="account-grid-chat">
                        <ChatContainer />
                    </div>
                </div>
            </main>
        </div>
        </FriendsProvider>
    )
}

export default HomePage
