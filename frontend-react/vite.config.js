import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg'],
      manifest: {
        name: 'WMS Mobile',
        short_name: 'WMS',
        description: 'Coletor móvel do WMS',
        theme_color: '#111827',
        background_color: '#eef1f5',
        display: 'standalone',
        start_url: '/mobile-react/',
        scope: '/mobile-react/',
        icons: [
          { src: '/mobile-react/pwa-192.png', sizes: '192x192', type: 'image/png' },
          { src: '/mobile-react/pwa-512.png', sizes: '512x512', type: 'image/png' }
        ]
      }
    })
  ],
  base: '/mobile-react/'
})
