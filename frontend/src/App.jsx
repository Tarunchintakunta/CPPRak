import { Routes, Route } from 'react-router-dom'
import Navbar from './components/common/Navbar'
import ProtectedRoute from './components/common/ProtectedRoute'
import Home from './pages/Home'
import Login from './pages/Login'
import Register from './pages/Register'
import Events from './pages/Events'
import EventDetail from './pages/EventDetail'
import MyTickets from './pages/MyTickets'
import TicketDetail from './pages/TicketDetail'
import AdminDashboard from './pages/AdminDashboard'
import CreateEvent from './pages/CreateEvent'
import ScanTicket from './pages/ScanTicket'

function App() {
  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#faf9f7' }}>
      <Navbar />
      <main className="flex-1 flex flex-col">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/events" element={<Events />} />
          <Route path="/events/:id" element={<EventDetail />} />
          <Route path="/my-tickets" element={
            <ProtectedRoute><MyTickets /></ProtectedRoute>
          } />
          <Route path="/tickets/:id" element={
            <ProtectedRoute><TicketDetail /></ProtectedRoute>
          } />
          <Route path="/admin" element={
            <ProtectedRoute adminOnly><AdminDashboard /></ProtectedRoute>
          } />
          <Route path="/admin/create-event" element={
            <ProtectedRoute adminOnly><CreateEvent /></ProtectedRoute>
          } />
          <Route path="/admin/scan" element={
            <ProtectedRoute adminOnly><ScanTicket /></ProtectedRoute>
          } />
        </Routes>
      </main>
      <footer className="border-t border-border-light py-8 text-center text-text-muted text-sm">
        <span className="font-medium text-text">Rakshan</span> &middot; Secure QR Ticketing &middot; 2026
      </footer>
    </div>
  )
}

export default App
