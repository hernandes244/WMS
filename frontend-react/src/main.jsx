import React from 'react'
import { createRoot } from 'react-dom/client'
import { registerSW } from 'virtual:pwa-register'
import './styles.css'
import App from './App.jsx'

registerSW({ immediate: true })

createRoot(document.getElementById('root')).render(
  <React.StrictMode><App /></React.StrictMode>
)
