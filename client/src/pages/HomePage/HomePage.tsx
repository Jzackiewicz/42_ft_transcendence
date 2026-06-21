import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv/BlinkingSpaceBGDiv'
import AccountHeader from './SubviewsHomePage/AccountHeader/AccountHeader'
import FriendsView from './SubviewsHomePage/FriendsView/FriendsView'
import ChatContainer from './SubviewsHomePage/ChatContainer/ChatContainer'
import { Navbar } from '../../components/Navbar/Navbar'

import styles from './HomePage.module.css'

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
        <div className={styles.homePageContainer}>
            <BlinkingSpaceBGDiv />

            {/* ── Nav ── */}
            <Navbar 
                actionButtonText="Logout"
                onActionButtonClick={handleLogout}
            />

            {/* ── Rules modal ── */}
            {showRulesModal && (
                <div
                    className={styles.rulesModalOverlay}
                    onClick={() => setShowRulesModal(false)}
                    role="dialog"
                    aria-modal="true"
                    aria-labelledby="rules-modal-title"
                >
                    <div className={styles.rulesModal} onClick={e => e.stopPropagation()}>
                        <button
                            className={styles.rulesModalClose}
                            onClick={() => setShowRulesModal(false)}
                            aria-label="Close rules"
                        >
                            ×
                        </button>
                        <h3 id="rules-modal-title" className={styles.rulesModalTitle}>
                            How to Play <span className={styles.rulesModalTitleAccent}>Quizscendence</span>
                        </h3>
                        <ul className={styles.rulesModalList}>
                            <li><strong>2–5 players.</strong> Everyone starts with <strong>❤️❤️❤️ lives</strong>.</li>
                            <li>On your turn, answer the question before the timer runs out.</li>
                            <li>Wrong answer or timeout = <strong>-1 life 💔</strong>. No lives = you're out.</li>
                            <li>Correct answer = <strong>+10 points</strong>, and you pick who answers next.</li>
                            <li>Pick yourself = <strong>+20 points</strong> if you're right (risky but worth it).</li>
                            <li>Keep nominating until someone else answers correctly.</li>
                        </ul>
                        <p className={styles.rulesModalWin}>
                            Be the last one alive, or earn the most points when the questions run out!
                        </p>
                    </div>
                </div>
            )}

            {/* ── Join modal ── */}
            {showJoinModal && (
                <div className={styles.joinModalOverlay}>
                    <div className={styles.joinModal}>
                        <h3 className={styles.joinModalTitle}>Join Lobby</h3>
                        <input
                            className={styles.joinModalInput}
                            type="text"
                            placeholder="Paste lobby UUID…"
                            value={joinUuid}
                            onChange={e => setJoinUuid(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && handleJoinLobby()}
                        />
                        <div className={styles.joinModalActions}>
                            <button className={styles.homeNavPlay} onClick={handleJoinLobby}>Join</button>
                            <button className={styles.joinModalCancel} onClick={() => setShowJoinModal(false)}>Cancel</button>
                        </div>
                    </div>
                </div>
            )}

            {/* ── Main ── */}
            <main className={styles.homeContent}>
                <AccountHeader
                    username={user?.username ?? ''}
                    email={user?.email ?? ''}
                    setShowJoinModal={setShowJoinModal}
                    setShowRulesModal={setShowRulesModal}
                    handleCreateLobby={handleCreateLobby}
                />

                <div className={styles.accountGrid}>
                    <FriendsView />

                    <div className={styles.accountGridChat}>
                        <ChatContainer />
                    </div>
                </div>
            </main>
        </div>
        </FriendsProvider>
    )
}

export default HomePage
