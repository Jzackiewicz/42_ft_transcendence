import { useState } from 'react'
import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv/BlinkingSpaceBGDiv'
import AccountHeader from './SubviewsHomePage/AccountHeader/AccountHeader'
import FriendsView from './SubviewsHomePage/FriendsView/FriendsView'
import StatsView from './SubviewsHomePage/StatsView/StatsView'
import ChatContainer from './SubviewsHomePage/ChatContainer/ChatContainer'
import { Navbar } from '../../components/Navbar/Navbar'
import UserProfileModal from '../../components/UserProfileModal/UserProfileModal'
import { PublicUser } from '../../types/User'
import { Button } from '../../components/Button/Button'
import { Modal } from '../../components/Modal/Modal'
import { Icon } from '../../components/Icon/Icon'
import ErrorBanner from '../../components/ErrorBanner/ErrorBanner'
import InlineError from '../../components/InlineError/InlineError'
import styles from './HomePage.module.css'
import { useHomePage, UUID_LENGTH } from './useHomePage'
import { FriendsProvider } from '../../context/FriendsListContext'

export function HomePage() {
    const {
        user,
        setUser,
        handleLogout,
        handleCreateLobby,
        handleJoinLobby,
        joinUuid, setJoinUuid,
        joinError, setJoinError,
        createError, setCreateError,
        showJoinModal, setShowJoinModal,
        showRulesModal, setShowRulesModal,
    } = useHomePage()
    const [selectedUser, setSelectedUser] = useState<PublicUser | null>(null)

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
                    <li><strong>2–5 players.</strong> Everyone starts with <strong className={styles.rulesLives}><Icon name="heart" size="sm" /><Icon name="heart" size="sm" /><Icon name="heart" size="sm" /> lives</strong>.</li>
                    <li>On your turn, answer the question before the timer runs out.</li>
                    <li>Wrong answer or timeout = <strong className={styles.rulesLives}>-1 life <Icon name="heartOutline" size="sm" /></strong>. No lives = you're out.</li>
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
                <InlineError message={joinError} />
                <input
                    className={styles.joinModalInput}
                    type="text"
                    placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000"
                    maxLength={UUID_LENGTH}
                    value={joinUuid}
                    autoFocus
                    onChange={e => { setJoinUuid(e.target.value); setJoinError(null) }}
                    onKeyDown={e => e.key === 'Enter' && handleJoinLobby()}
                />
                <div className={styles.joinModalActions}>
                    <Button onClick={handleJoinLobby} disabled={!joinUuid.trim()}>Join</Button>
                    <Button variant="ghost" onClick={() => setShowJoinModal(false)}>Cancel</Button>
                </div>
            </Modal>

            {/* ── User profile modal ── */}
            {selectedUser && (
                <UserProfileModal user={selectedUser} onClose={() => setSelectedUser(null)} />
            )}

            {/* ── Main ── */}
            <main className={styles.homeContent}>
                {createError && <ErrorBanner message={createError} onDismiss={() => setCreateError(null)} />}
                <AccountHeader
                    user={user}
                    setUser={setUser}
                    setShowJoinModal={setShowJoinModal}
                    setShowRulesModal={setShowRulesModal}
                    handleCreateLobby={handleCreateLobby}
                />

                <div className={styles.accountGrid}>
                    <FriendsView onSelectUser={setSelectedUser} />
                    <StatsView />

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
