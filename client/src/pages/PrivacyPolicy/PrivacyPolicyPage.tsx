import React from 'react';
import { Link } from 'react-router-dom';
import BlinkingSpaceBGDiv from '../../components/BlinkingSpaceBGDiv/BlinkingSpaceBGDiv';
import styles from './PrivacyPolicy.module.css';

export function PrivacyPolicyPage() {
	return (
		<div className={styles['static-page-container']}>
			<BlinkingSpaceBGDiv />
			<div className={styles['static-page-content']}>
				<Link to="/" className={styles['back-button']}>
					← Go Back
				</Link>
				<h1>Privacy Policy</h1>
				<p className={styles['last-updated']}>Last Updated: June 2026</p>

				<h2>1. Information We Collect</h2>
				<p>We collect information you provide directly to us when you create an account, such as your username, email address, and password. We also collect data related to your gameplay and social interactions on the platform.</p>

				<h2>2. How We Use Your Information</h2>
				<p>We use the collected information to:</p>
				<ul>
					<li>Provide, maintain, and improve our services.</li>
					<li>Facilitate matchmaking and gameplay.</li>
					<li>Enable social features like chat and friend requests.</li>
					<li>Protect the security of our users and services.</li>
				</ul>

				<h2>3. Data Security</h2>
				<p>We implement appropriate technical and organizational measures to protect your personal data against unauthorized access, loss, or alteration.</p>

				<h2>4. Your Rights</h2>
				<p>You have the right to access, update, or delete your account information at any time through your profile settings.</p>

				<h2>5. Contact Us</h2>
				<p>If you have questions about this Privacy Policy, please contact the Transcendence team.</p>
			</div>
		</div>
	);
}
