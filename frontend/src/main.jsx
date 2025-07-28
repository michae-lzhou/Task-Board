/*******************************************************************************
 * main.jsx
 * Purpose: Entry point for React app that attaches the root component (App)
 *          to the DOM and wraps it in React's StrictMode for highlighting
 *          potential problems during development.
 ******************************************************************************/

import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Attach React app to DOM element with id 'root' and enable StrictMode
createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
