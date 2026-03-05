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
    <div className="min-h-screen flex flex-col bg-bg">
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
      <footer className="border-t border-surface-lighter py-6 text-center text-text-muted text-sm">
        Rakshan &copy; 2026 &mdash; Secure QR Ticket Management
      </footer>
    </div>
  )
}

export default App
