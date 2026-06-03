import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/account': {
        target: 'http://127.0.0.1:8000',
        secure: false,
        changeOrigin: true,
      },
      '/game': {
        target: 'http://127.0.0.1:8000',
        secure: false,
        changeOrigin: true,
      },
      '/social': {
        target: 'http://127.0.0.1:8000',
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
