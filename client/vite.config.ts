import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
	plugins: [react()],
	server: {
		proxy: {
      '/api': {
        target: 'https://localhost:8000',
				secure: false,
				changeOrigin: true,
			},
			'/ws': {
				target: 'ws://127.0.0.1:8000',
				ws: true,
				secure: false,
				changeOrigin: true,
			},
		}
	}
})
