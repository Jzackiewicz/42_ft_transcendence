
import { Link } from 'react-router-dom';
import styles from './Footer.module.css';

export function Footer() {
	return (
		<footer className={styles.footer}>
			<nav className={styles.nav}>
				<Link to="/privacy" className={styles.link}>Privacy Policy</Link>
				<Link to="/terms" className={styles.link}>Terms of Service</Link>
			</nav>
			<p className={styles.copyright}>&copy; 2026 Transcendence Team</p>
		</footer>
	);
}
