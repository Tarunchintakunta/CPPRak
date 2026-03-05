import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Shield, LogOut, Menu, X, Ticket, Calendar, LayoutDashboard } from 'lucide-react';
import { useState } from 'react';

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-surface border-b border-surface-lighter sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center gap-2 text-primary font-bold text-xl no-underline">
            <Shield className="w-7 h-7" />
            Rakshan
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-6">
            <Link to="/events" className="text-text-muted hover:text-text no-underline flex items-center gap-1.5 text-sm font-medium transition-colors">
              <Calendar className="w-4 h-4" /> Events
            </Link>
            {user && (
              <Link to="/my-tickets" className="text-text-muted hover:text-text no-underline flex items-center gap-1.5 text-sm font-medium transition-colors">
                <Ticket className="w-4 h-4" /> My Tickets
              </Link>
            )}
            {isAdmin && (
              <Link to="/admin" className="text-text-muted hover:text-text no-underline flex items-center gap-1.5 text-sm font-medium transition-colors">
                <LayoutDashboard className="w-4 h-4" /> Admin
              </Link>
            )}
            {user ? (
              <div className="flex items-center gap-4">
                <span className="text-sm text-text-muted">{user.name}</span>
                <button onClick={handleLogout} className="flex items-center gap-1.5 text-sm text-danger hover:text-red-400 bg-transparent border-none cursor-pointer font-medium">
                  <LogOut className="w-4 h-4" /> Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <Link to="/login" className="text-sm text-text-muted hover:text-text no-underline font-medium">Login</Link>
                <Link to="/register" className="text-sm bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-lg no-underline font-medium transition-colors">Register</Link>
              </div>
            )}
          </div>

          {/* Mobile hamburger */}
          <button onClick={() => setOpen(!open)} className="md:hidden bg-transparent border-none text-text cursor-pointer p-1">
            {open ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="md:hidden bg-surface-light border-t border-surface-lighter px-4 py-4 flex flex-col gap-3">
          <Link to="/events" onClick={() => setOpen(false)} className="text-text-muted hover:text-text no-underline text-sm font-medium">Events</Link>
          {user && <Link to="/my-tickets" onClick={() => setOpen(false)} className="text-text-muted hover:text-text no-underline text-sm font-medium">My Tickets</Link>}
          {isAdmin && <Link to="/admin" onClick={() => setOpen(false)} className="text-text-muted hover:text-text no-underline text-sm font-medium">Admin</Link>}
          {user ? (
            <button onClick={() => { handleLogout(); setOpen(false); }} className="text-left text-sm text-danger bg-transparent border-none cursor-pointer font-medium">Logout</button>
          ) : (
            <>
              <Link to="/login" onClick={() => setOpen(false)} className="text-text-muted hover:text-text no-underline text-sm font-medium">Login</Link>
              <Link to="/register" onClick={() => setOpen(false)} className="text-primary no-underline text-sm font-medium">Register</Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
