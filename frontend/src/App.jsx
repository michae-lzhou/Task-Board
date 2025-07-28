/*******************************************************************************
 * App.jsx
 * Purpose: Entry point of the React application that renders the main Dashboard
 *          component within a container div.
 ******************************************************************************/

import Dashboard from './pages/Dashboard'
import './App.css'

function App() {
  return (
    <div className="App">
      {/* Render the Dashboard component */}
      <Dashboard />
    </div>
  )
}

export default App
