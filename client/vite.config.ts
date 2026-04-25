import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/account': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
      },
      '/game': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
      },
      '/social': {
        target: 'https://localhost:8443',
        secure: false,
        changeOrigin: true,
      },
    }

  }
})
