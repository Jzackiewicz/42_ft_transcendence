import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv'
import { useHomePage } from './useHomePage'
import AccountHeader from './SubviewsHomePage/AccountHeader/AccountHeader'
import FriendsView from './SubviewsHomePage/FriendsView/FriendsView'
import StatsView from './SubviewsHomePage/StatsView/StatsView'
import ChatContainer from './SubviewsHomePage/ChatContainer/ChatContainer'
import { FriendsProvider } from '../../context/FriendsListContext'
import './HomePage.css'

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
            <nav className="home-nav">
                <div className="home-nav-logo"><span className="logo-quiz">QUIZ</span>SENDENCE</div>
                <div className="home-nav-space" />
                <button className="home-nav-play" onClick={handleLogout}>Logout</button>
            </nav>

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
                    <StatsView />

                    <div className="account-grid-chat">
                        <ChatContainer />
                    </div>
                </div>
            </main>

            {/* ── Footer ── */}
            <footer className="home-footer">
                <a className="home-footer-link" href="/privacy-policy">Privacy Policy</a>
                <span className="home-footer-sep" />
                <a className="home-footer-link" href="/terms-of-use">Terms of Use</a>
            </footer>
        </div>
        </FriendsProvider>
    )
}

export default HomePage
