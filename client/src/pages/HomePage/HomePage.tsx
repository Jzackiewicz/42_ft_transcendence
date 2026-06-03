import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv'
import { useHomePage } from './useHomePage'
import AccountHeader from './SubviewsHomePage/AccountHeader/AccountHeader'
import FriendsView from './SubviewsHomePage/FriendsView/FriendsView'
import StatsView from './SubviewsHomePage/StatsView/StatsView'
import ChatContainer from './SubviewsHomePage/ChatContainer/ChatContainer'
import './HomePage.css'

function HomePage() {
    const { user, handleLogout } = useHomePage()

    return (
        <div className="home-page-container">
            <BlinkingSpaceBGDiv />

            {/* ── Nav ── */}
            <nav className="home-nav">
                <div className="home-nav-logo"><span className="logo-quiz">QUIZ</span>SENDENCE</div>
                <div className="home-nav-space" />
                <button className="home-nav-play">▶ Play Now</button>
            </nav>

            {/* ── Main ── */}
            <main className="home-content">
                <AccountHeader
                    username={user?.username ?? ''}
                    email={user?.email ?? ''}
                    onLogout={handleLogout}
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
    )
}

export default HomePage
