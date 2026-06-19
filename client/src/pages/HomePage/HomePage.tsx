import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv'
import AccountHeader from './SubviewsHomePage/AccountHeader/AccountHeader'
import FriendsView from './SubviewsHomePage/FriendsView/FriendsView'
import ChatContainer from './SubviewsHomePage/ChatContainer/ChatContainer'
import SolarSystem from './SubviewsHomePage/Solar/SolarSystem'

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
        showRulesModal, setShowRulesModal,
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

            {/* ── Rules modal ── */}
            {showRulesModal && (
                <div
                    className="rules-modal-overlay"
                    onClick={() => setShowRulesModal(false)}
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="rules-modal-title"
                >
                    <div className="rules-modal" onClick={e => e.stopPropagation()}>
                        <button
                            className="rules-modal-close"
                            onClick={() => setShowRulesModal(false)}
                            aria-label="Close rules"
                        >
                            ×
                        </button>
                        <h3 id="rules-modal-title" className="rules-modal-title">
                            How to Play <span className="rules-modal-title-accent">Quizscendence</span>
                        </h3>
                        <ul className="rules-modal-list">
                            <li><strong>2–5 players.</strong> Everyone starts with <strong>❤️❤️❤️ lives</strong>.</li>
                            <li>On your turn, answer the question before the timer runs out.</li>
                            <li>Wrong answer or timeout = <strong>-1 life 💔</strong>. No lives = you're out.</li>
                            <li>Correct answer = <strong>+10 points</strong>, and you pick who answers next.</li>
                            <li>Pick yourself = <strong>+20 points</strong> if you're right (risky but worth it).</li>
                            <li>Keep nominating until someone else answers correctly.</li>
                        </ul>
                        <p className="rules-modal-win">
                            Be the last one alive, or earn the most points when the questions run out!
                        </p>
                    </div>
                </div>
            )}

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
                    setShowRulesModal={setShowRulesModal}
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
