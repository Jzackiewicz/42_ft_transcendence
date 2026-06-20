import { Link } from 'react-router-dom';
import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv/BlinkingSpaceBGDiv';
import styles from '../static-page.module.css';

export function TermsOfServicePage() {
	return (
		<div className={styles['static-page-container']}>
			<BlinkingSpaceBGDiv />
			<div className={styles['static-page-content']}>
				<Link to="/" className={styles['back-button']}>
					← Go Back
				</Link>
				<h1>Terms of Service</h1>
				<p className={styles['last-updated']}>Last Updated: June 2026</p>

				<h2>1. Acceptance of Terms</h2>
				<p>By accessing or using Transcendence, you agree to be bound by these Terms of Service and all applicable laws and regulations.</p>

				<h2>2. User Accounts</h2>
				<p>You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You must notify us immediately of any unauthorized use.</p>

				<h2>3. Code of Conduct</h2>
				<p>Users agree not to:</p>
				<ul>
					<li>Cheat, exploit, or use unauthorized third-party software.</li>
					<li>Harass, abuse, or threaten other players.</li>
					<li>Post offensive, illegal, or inappropriate content.</li>
					<li>Attempt to interfere with the proper functioning of the service.</li>
				</ul>

				<h2>4. Intellectual Property</h2>
				<p>All content and materials available on Transcendence are the property of the project creators and are protected by applicable intellectual property laws.</p>

				<h2>5. Termination</h2>
				<p>We reserve the right to suspend or terminate your account at our discretion for violations of these terms.</p>

				<h2>6. Disclaimer</h2>
				<p>The service is provided "as is" without warranties of any kind. We are not liable for any damages arising from your use of the service.</p>
			</div>
		</div>
	);
}
