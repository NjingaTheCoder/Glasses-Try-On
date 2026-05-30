import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import StoreProducts from './pages/StoreProducts'
import TryOn from './pages/TryOn'

function App() {
  const isAuthenticated = !!localStorage.getItem('access_token')

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/dashboard"
          element={isAuthenticated ? <Dashboard /> : <Navigate to="/login" />}
        />
        <Route
          path="/store/:id/products"
          element={isAuthenticated ? <StoreProducts /> : <Navigate to="/login" />}
        />
        <Route path="/tryon" element={isAuthenticated ? <TryOn /> : <Navigate to="/login" />} />
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
