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

  const statusIcon = (status) => {
    if (status === 'confirmed') return <CheckCircle className="w-4 h-4 text-success" />;
    if (status === 'cancelled') return <XCircle className="w-4 h-4 text-danger" />;
    return <AlertCircle className="w-4 h-4 text-accent" />;
  };

  const statusColor = (status) => {
    if (status === 'confirmed') return 'bg-success/10 text-success';
    if (status === 'cancelled') return 'bg-danger/10 text-danger';
    return 'bg-accent/10 text-accent';
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <h1 className="text-3xl font-bold mb-8">My Tickets</h1>

      {registrations.length === 0 ? (
        <div className="text-center py-20">
          <Ticket className="w-16 h-16 text-text-muted/30 mx-auto mb-4" />
          <p className="text-text-muted text-lg mb-4">No tickets yet</p>
          <Link to="/events" className="text-primary hover:text-primary-light no-underline font-medium">Browse events</Link>
        </div>
      ) : (
        <div className="space-y-4">
          {registrations.map((reg) => (
            <div key={reg.registration_id} className="bg-surface rounded-2xl border border-surface-lighter p-6 flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="text-lg font-semibold truncate">{reg.event_name || 'Event'}</h3>
                  <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor(reg.status)}`}>
                    {statusIcon(reg.status)} {reg.status}
                  </span>
                </div>
                <div className="flex flex-wrap gap-4 text-sm text-text-muted">
                  {reg.event_date && (
                    <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" /> {reg.event_date}</span>
                  )}
                  {reg.event_location && (
                    <span className="flex items-center gap-1"><MapPin className="w-3.5 h-3.5" /> {reg.event_location}</span>
                  )}
                  {reg.checked_in && (
                    <span className="flex items-center gap-1 text-success"><CheckCircle className="w-3.5 h-3.5" /> Checked in</span>
                  )}
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                {reg.status === 'confirmed' && reg.ticket && (
                  <Link
                    to={`/tickets/${reg.ticket.ticket_id}`}
                    className="inline-flex items-center gap-1.5 bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded-lg text-sm font-medium no-underline transition-colors"
                  >
                    <Ticket className="w-4 h-4" /> View Ticket
                  </Link>
                )}
                {reg.status === 'confirmed' && (
                  <button
                    onClick={() => handleCancel(reg.registration_id)}
                    disabled={cancelling === reg.registration_id}
                    className="text-sm text-danger hover:text-red-400 bg-transparent border border-danger/30 hover:border-danger/50 px-4 py-2 rounded-lg cursor-pointer font-medium transition-colors disabled:opacity-50"
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
