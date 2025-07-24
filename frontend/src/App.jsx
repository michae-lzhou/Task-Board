import { useEffect, useState } from 'react'
import axios from 'axios'

function App() {
  const [data, setData] = useState(null)

  useEffect(() => {
    axios.get('http://localhost:8000/')
      .then(res => setData(res.data))
  }, [])

  return <h1>{data?.message || 'Loading...'}</h1>
}

export default App;
