import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv/BlinkingSpaceBGDiv'
import AccountHeader from './SubviewsHomePage/AccountHeader/AccountHeader'
import FriendsView from './SubviewsHomePage/FriendsView/FriendsView'
import ChatContainer from './SubviewsHomePage/ChatContainer/ChatContainer'
import SolarSystem from './SubviewsHomePage/Solar/SolarSystem'
import { Navbar } from '../../components/Navbar/Navbar'
import { Button } from '../../components/Button/Button'
import { Modal } from '../../components/Modal/Modal'

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
            <Modal
                open={showRulesModal}
                onClose={() => setShowRulesModal(false)}
                title={<>How to Play <span className={styles.rulesModalTitleAccent}>Quizscendence</span></>}
            >
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
            </Modal>

            {/* ── Join modal ── */}
            <Modal
                open={showJoinModal}
                onClose={() => setShowJoinModal(false)}
                title="Join Lobby"
            >
                <input
                    className={styles.joinModalInput}
                    type="text"
                    placeholder="Paste lobby UUID…"
                    value={joinUuid}
                    onChange={e => setJoinUuid(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && handleJoinLobby()}
                />
                <div className={styles.joinModalActions}>
                    <Button onClick={handleJoinLobby}>Join</Button>
                    <Button variant="ghost" onClick={() => setShowJoinModal(false)}>Cancel</Button>
                </div>
            </Modal>

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
                    <SolarSystem />

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
