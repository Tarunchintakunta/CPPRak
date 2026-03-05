import { useState } from 'react';
import { ticketsAPI } from '../services/api';
import { ScanLine, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

export default function ScanTicket() {
  const [qrData, setQrData] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleValidate = async (e) => {
    e.preventDefault();
    if (!qrData.trim()) return;
    setLoading(true);
    setResult(null);
    setError('');
    try {
      const res = await ticketsAPI.validate(qrData.trim());
      setResult(res.data);
    } catch (err) {
      const data = err.response?.data;
      if (data?.error_code) {
        setResult(data);
      } else {
        setError(data?.error || 'Validation failed');
      }
    } finally {
      setLoading(false);
    }
  };

  const isValid = result?.valid === true;
  const isUsed = result?.error_code === 'TICKET_ALREADY_USED';

  return (
    <div className="max-w-lg mx-auto px-4 sm:px-6 py-10">
      <h1 className="text-3xl font-bold mb-2">Validate Ticket</h1>
      <p className="text-text-muted mb-8">Paste the scanned QR code data to validate a ticket.</p>

      <form onSubmit={handleValidate} className="bg-surface rounded-2xl border border-surface-lighter p-6 mb-6">
        <label className="block text-sm font-medium text-text-muted mb-2">QR Code Data</label>
        <textarea
          value={qrData} onChange={(e) => setQrData(e.target.value)}
          rows={4}
          className="w-full bg-surface-light border border-surface-lighter rounded-lg py-3 px-4 text-text placeholder-text-muted/50 focus:outline-none focus:border-primary font-mono text-sm resize-none"
          placeholder="Paste QR code data here..."
        />
        <button
          type="submit" disabled={loading || !qrData.trim()}
          className="mt-4 w-full inline-flex items-center justify-center gap-2 bg-primary hover:bg-primary-dark disabled:opacity-50 text-white font-semibold py-3 rounded-xl transition-colors cursor-pointer border-none text-base"
        >
          <ScanLine className="w-5 h-5" />
          {loading ? 'Validating...' : 'Validate Ticket'}
        </button>
      </form>

      {result && (
        <div className={`rounded-2xl border p-6 ${isValid ? 'bg-success/5 border-success/30' : isUsed ? 'bg-accent/5 border-accent/30' : 'bg-danger/5 border-danger/30'}`}>
          <div className="flex items-center gap-3 mb-4">
            {isValid ? (
              <CheckCircle className="w-8 h-8 text-success" />
            ) : isUsed ? (
              <AlertCircle className="w-8 h-8 text-accent" />
            ) : (
              <XCircle className="w-8 h-8 text-danger" />
            )}
            <div>
              <h3 className={`text-lg font-semibold ${isValid ? 'text-success' : isUsed ? 'text-accent' : 'text-danger'}`}>
                {isValid ? 'Ticket Valid' : result.error_code || 'Invalid Ticket'}
              </h3>
              <p className="text-sm text-text-muted">{result.message || ''}</p>
            </div>
          </div>
          {result.ticket && (
            <div className="space-y-2 text-sm border-t border-surface-lighter pt-4 mt-2">
              <div className="flex justify-between"><span className="text-text-muted">Ticket ID</span><span className="font-mono text-xs">{result.ticket.ticket_id?.slice(0, 16)}...</span></div>
              {result.ticket.event_name && <div className="flex justify-between"><span className="text-text-muted">Event</span><span>{result.ticket.event_name}</span></div>}
              <div className="flex justify-between"><span className="text-text-muted">Status</span><span className="font-medium">{result.ticket.status}</span></div>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 bg-danger/10 text-danger px-4 py-3 rounded-lg text-sm">
          <AlertCircle className="w-4 h-4 shrink-0" /> {error}
        </div>
      )}
    </div>
  );
}
