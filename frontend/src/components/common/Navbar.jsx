import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { LogOut, Menu, X, Ticket, Calendar, LayoutDashboard } from 'lucide-react';
import { useState } from 'react';

export default function Navbar() {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  const navLink = (to, label, Icon) => (
    <Link
      to={to}
      className={`flex items-center gap-1.5 text-sm font-medium no-underline transition-colors ${
        isActive(to) ? 'text-accent' : 'text-text-mid hover:text-text'
      }`}
    >
      <Icon className="w-4 h-4" /> {label}
    </Link>
  );

  return (
    <nav className="bg-white border-b border-border-light sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <Link to="/" className="flex items-center gap-2 no-underline">
            <div className="w-7 h-7 bg-primary rounded-md flex items-center justify-center">
              <span className="text-white text-xs font-bold tracking-tight">R</span>
            </div>
            <span className="font-semibold text-text text-base tracking-tight">Rakshan</span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            {navLink('/events', 'Events', Calendar)}
            {user && navLink('/my-tickets', 'My Tickets', Ticket)}
            {isAdmin && navLink('/admin', 'Admin', LayoutDashboard)}

            {user ? (
              <div className="flex items-center gap-4 ml-2 pl-4 border-l border-border-light">
                <span className="text-sm text-text-muted">{user.name}</span>
                <button onClick={handleLogout} className="flex items-center gap-1 text-sm text-text-muted hover:text-danger bg-transparent border-none cursor-pointer">
                  <LogOut className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2 ml-2 pl-4 border-l border-border-light">
                <Link to="/login" className="text-sm text-text-mid hover:text-text no-underline font-medium">Log in</Link>
                <Link to="/register" className="text-sm bg-primary hover:bg-primary-dark text-white px-3.5 py-1.5 rounded-md no-underline font-medium transition-colors">Sign up</Link>
              </div>
            )}
          </div>

          <button onClick={() => setOpen(!open)} className="md:hidden bg-transparent border-none text-text cursor-pointer p-1">
            {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {open && (
        <div className="md:hidden bg-white border-t border-border-light px-4 py-3 flex flex-col gap-2.5">
          <Link to="/events" onClick={() => setOpen(false)} className="text-text-mid hover:text-text no-underline text-sm font-medium py-1">Events</Link>
          {user && <Link to="/my-tickets" onClick={() => setOpen(false)} className="text-text-mid hover:text-text no-underline text-sm font-medium py-1">My Tickets</Link>}
          {isAdmin && <Link to="/admin" onClick={() => setOpen(false)} className="text-text-mid hover:text-text no-underline text-sm font-medium py-1">Admin</Link>}
          {user ? (
            <button onClick={() => { handleLogout(); setOpen(false); }} className="text-left text-sm text-danger bg-transparent border-none cursor-pointer font-medium py-1">Log out</button>
          ) : (
            <>
              <Link to="/login" onClick={() => setOpen(false)} className="text-text-mid hover:text-text no-underline text-sm font-medium py-1">Log in</Link>
              <Link to="/register" onClick={() => setOpen(false)} className="text-accent no-underline text-sm font-medium py-1">Sign up</Link>
            </>
          )}
        </div>
      )}
    </nav>
  );
}
