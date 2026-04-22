import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { viteStaticCopy } from 'vite-plugin-static-copy'
import path from 'path'

export default defineConfig({
  plugins: [
    react(),
    // Copy all MediaPipe WASM / binary assets so they're served under /mediapipe/
    viteStaticCopy({
      targets: [
        {
          src: 'node_modules/@mediapipe/face_mesh/*',
          dest: 'mediapipe',
        },
      ],
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  optimizeDeps: {
    include: ['@mediapipe/face_mesh'],
  },
})
