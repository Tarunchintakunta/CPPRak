import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { registrationsAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Ticket, Calendar, MapPin, XCircle, CheckCircle, AlertCircle } from 'lucide-react';

export default function MyTickets() {
  const [registrations, setRegistrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(null);

  const fetchRegistrations = () => {
    setLoading(true);
    registrationsAPI.list()
      .then((res) => setRegistrations(res.data.registrations || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchRegistrations(); }, []);

  const handleCancel = async (regId) => {
    if (!confirm('Cancel this registration? Your ticket will be revoked.')) return;
    setCancelling(regId);
    try {
      await registrationsAPI.cancel(regId);
      fetchRegistrations();
    } catch {
      alert('Failed to cancel registration');
    } finally {
      setCancelling(null);
    }
  };

  if (loading) return <LoadingSpinner text="Loading your tickets..." />;

  const statusBadge = (status) => {
    if (status === 'confirmed') return 'text-success bg-emerald-50 border-emerald-100';
    if (status === 'cancelled') return 'text-danger bg-red-50 border-red-100';
    return 'text-amber-600 bg-amber-50 border-amber-100';
  };

  const statusIcon = (status) => {
    if (status === 'confirmed') return <CheckCircle className="w-3 h-3" />;
    if (status === 'cancelled') return <XCircle className="w-3 h-3" />;
    return <AlertCircle className="w-3 h-3" />;
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-2xl font-bold mb-6">My Tickets</h1>

      {registrations.length === 0 ? (
        <div className="text-center py-20">
          <Ticket className="w-10 h-10 text-border mx-auto mb-3" />
          <p className="text-text-muted mb-3">No tickets yet</p>
          <Link to="/events" className="text-accent hover:text-accent-light no-underline text-sm font-medium">Browse events</Link>
        </div>
      ) : (
        <div className="space-y-3">
          {registrations.map((reg) => (
            <div key={reg.registration_id} className="bg-white rounded-lg border border-border-light p-4 flex flex-col sm:flex-row sm:items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1.5">
                  <h3 className="text-sm font-semibold truncate">{reg.event_name || 'Event'}</h3>
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium border ${statusBadge(reg.status)}`}>
                    {statusIcon(reg.status)} {reg.status}
                  </span>
                </div>
                <div className="flex flex-wrap gap-3 text-xs text-text-muted">
                  {reg.event_date && (
                    <span className="flex items-center gap-1"><Calendar className="w-3 h-3" /> {reg.event_date}</span>
                  )}
                  {reg.event_location && (
                    <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {reg.event_location}</span>
                  )}
                  {reg.checked_in && (
                    <span className="flex items-center gap-1 text-success"><CheckCircle className="w-3 h-3" /> Checked in</span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {reg.status === 'confirmed' && reg.ticket && (
                  <Link
                    to={`/tickets/${reg.ticket.ticket_id}`}
                    className="inline-flex items-center gap-1.5 bg-primary hover:bg-primary-dark text-white px-3 py-1.5 rounded-md text-xs font-medium no-underline transition-colors"
                  >
                    <Ticket className="w-3.5 h-3.5" /> View Ticket
                  </Link>
                )}
                {reg.status === 'confirmed' && (
                  <button
                    onClick={() => handleCancel(reg.registration_id)}
                    disabled={cancelling === reg.registration_id}
                    className="text-xs text-danger hover:text-red-700 bg-transparent border border-red-200 hover:border-red-300 px-3 py-1.5 rounded-md cursor-pointer font-medium transition-colors disabled:opacity-50"
                  >
                    {cancelling === reg.registration_id ? 'Cancelling...' : 'Cancel'}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
