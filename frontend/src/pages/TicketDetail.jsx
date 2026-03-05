import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ticketsAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { ArrowLeft, QrCode, Calendar, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function TicketDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    ticketsAPI.get(id)
      .then((res) => setTicket(res.data.ticket))
      .catch((err) => setError(err.response?.data?.error || 'Ticket not found'))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <LoadingSpinner text="Loading ticket..." />;
  if (error || !ticket) return (
    <div className="max-w-3xl mx-auto px-4 py-20 text-center">
      <p className="text-text-muted text-lg">{error || 'Ticket not found'}</p>
    </div>
  );

  const statusConfig = {
    valid: { icon: CheckCircle, color: 'text-success', bg: 'bg-success/10', label: 'Valid' },
    used: { icon: AlertCircle, color: 'text-accent', bg: 'bg-accent/10', label: 'Used' },
    revoked: { icon: XCircle, color: 'text-danger', bg: 'bg-danger/10', label: 'Revoked' },
  };
  const st = statusConfig[ticket.status] || statusConfig.valid;
  const StIcon = st.icon;

  return (
    <div className="max-w-lg mx-auto px-4 sm:px-6 py-10">
      <button onClick={() => navigate('/my-tickets')} className="flex items-center gap-1.5 text-text-muted hover:text-text text-sm mb-6 bg-transparent border-none cursor-pointer font-medium">
        <ArrowLeft className="w-4 h-4" /> Back to my tickets
      </button>

      <div className="bg-surface rounded-2xl border border-surface-lighter overflow-hidden">
        {/* QR Code */}
        <div className="bg-white p-8 flex items-center justify-center">
          {ticket.status === 'valid' ? (
            <img
              src={ticketsAPI.getQrUrl(ticket.ticket_id)}
              alt="QR Code"
              className="w-64 h-64 object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
          ) : null}
          <div className={`w-64 h-64 flex flex-col items-center justify-center ${ticket.status === 'valid' ? 'hidden' : ''}`}>
            <QrCode className="w-24 h-24 text-gray-300 mb-2" />
            <p className="text-gray-500 text-sm">
              {ticket.status === 'valid' ? 'QR code loading...' : `Ticket ${ticket.status}`}
            </p>
          </div>
        </div>

        {/* Details */}
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold">{ticket.event_name || 'Event Ticket'}</h2>
            <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${st.bg} ${st.color}`}>
              <StIcon className="w-4 h-4" /> {st.label}
            </span>
          </div>

          <div className="space-y-3 text-sm">
            <div className="flex justify-between py-2 border-b border-surface-lighter">
              <span className="text-text-muted">Ticket ID</span>
              <span className="font-mono text-xs">{ticket.ticket_id?.slice(0, 12)}...</span>
            </div>
            {ticket.event_id && (
              <div className="flex justify-between py-2 border-b border-surface-lighter">
                <span className="text-text-muted">Event ID</span>
                <span className="font-mono text-xs">{ticket.event_id?.slice(0, 12)}...</span>
              </div>
            )}
            <div className="flex justify-between py-2 border-b border-surface-lighter">
              <span className="text-text-muted">Created</span>
              <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5 text-text-muted" /> {new Date(ticket.created_at).toLocaleDateString()}</span>
            </div>
            {ticket.used_at && (
              <div className="flex justify-between py-2 border-b border-surface-lighter">
                <span className="text-text-muted">Used at</span>
                <span>{new Date(ticket.used_at).toLocaleString()}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
