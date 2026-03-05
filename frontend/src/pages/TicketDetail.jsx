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
      <p className="text-text-muted">{error || 'Ticket not found'}</p>
    </div>
  );

  const statusConfig = {
    valid: { icon: CheckCircle, color: 'text-success', bg: 'bg-emerald-50 border-emerald-100', label: 'Valid' },
    used: { icon: AlertCircle, color: 'text-amber-600', bg: 'bg-amber-50 border-amber-100', label: 'Used' },
    revoked: { icon: XCircle, color: 'text-danger', bg: 'bg-red-50 border-red-100', label: 'Revoked' },
  };
  const st = statusConfig[ticket.status] || statusConfig.valid;
  const StIcon = st.icon;

  return (
    <div className="max-w-sm mx-auto px-4 sm:px-6 py-10">
      <button onClick={() => navigate('/my-tickets')} className="flex items-center gap-1.5 text-text-muted hover:text-text text-sm mb-6 bg-transparent border-none cursor-pointer font-medium">
        <ArrowLeft className="w-4 h-4" /> My tickets
      </button>

      <div className="bg-white rounded-lg border border-border-light overflow-hidden">
        <div className="p-6 flex items-center justify-center bg-surface-alt border-b border-border-light">
          {ticket.status === 'valid' ? (
            <img
              src={ticketsAPI.getQrUrl(ticket.ticket_id)}
              alt="QR Code"
              className="w-52 h-52 object-contain"
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
          ) : null}
          <div className={`w-52 h-52 flex flex-col items-center justify-center ${ticket.status === 'valid' ? 'hidden' : ''}`}>
            <QrCode className="w-16 h-16 text-border mb-2" />
            <p className="text-text-muted text-xs">
              {ticket.status === 'valid' ? 'Loading...' : `Ticket ${ticket.status}`}
            </p>
          </div>
        </div>

        <div className="p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-text">{ticket.event_name || 'Event Ticket'}</h2>
            <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium border ${st.bg} ${st.color}`}>
              <StIcon className="w-3 h-3" /> {st.label}
            </span>
          </div>

          <div className="space-y-0 text-sm divide-y divide-border-light">
            <div className="flex justify-between py-2.5">
              <span className="text-text-muted text-xs">Ticket ID</span>
              <span className="font-mono text-[11px] text-text-mid">{ticket.ticket_id?.slice(0, 12)}...</span>
            </div>
            {ticket.event_id && (
              <div className="flex justify-between py-2.5">
                <span className="text-text-muted text-xs">Event ID</span>
                <span className="font-mono text-[11px] text-text-mid">{ticket.event_id?.slice(0, 12)}...</span>
              </div>
            )}
            <div className="flex justify-between py-2.5">
              <span className="text-text-muted text-xs">Created</span>
              <span className="flex items-center gap-1 text-xs text-text-mid"><Calendar className="w-3 h-3" /> {new Date(ticket.created_at).toLocaleDateString()}</span>
            </div>
            {ticket.used_at && (
              <div className="flex justify-between py-2.5">
                <span className="text-text-muted text-xs">Used at</span>
                <span className="text-xs text-text-mid">{new Date(ticket.used_at).toLocaleString()}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
