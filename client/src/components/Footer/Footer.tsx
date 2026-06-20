import React from 'react';
import { Link } from 'react-router-dom';

export function Footer() {
	return (
		<footer style={{
			padding: '20px',
			marginTop: 'auto',
			textAlign: 'center',
			borderTop: '1px solid rgba(255, 255, 255, 0.1)',
			fontSize: '0.9rem'
		}}>
			<nav style={{ display: 'flex', justifyContent: 'center', gap: '20px' }}>
				<Link to="/privacy" style={{ color: '#aaa', textDecoration: 'none' }}>Privacy Policy</Link>
				<Link to="/terms" style={{ color: '#aaa', textDecoration: 'none' }}>Terms of Service</Link>
			</nav>
			<p style={{ color: '#555', marginTop: '10px' }}>&copy; 2026 Transcendence Team</p>
		</footer>
	);
}
