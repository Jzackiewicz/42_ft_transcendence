import { useHomePage } from './useHomePage'

function HomePage() {
    const { user, handleLogout } = useHomePage()

    return (
        <div className="home-page-container">
            <h1>Home page</h1>
            <button onClick={handleLogout}>Logout: {user?.username}</button>
        </div>
    )
}

export default HomePage