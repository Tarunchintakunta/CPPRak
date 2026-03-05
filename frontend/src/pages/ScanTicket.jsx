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
    <div className="max-w-md mx-auto px-4 sm:px-6 py-10">
      <h1 className="text-2xl font-bold mb-1">Validate Ticket</h1>
      <p className="text-text-muted text-sm mb-6">Paste scanned QR code data below.</p>

      <form onSubmit={handleValidate} className="bg-white rounded-lg border border-border-light p-5 mb-4">
        <label className="block text-sm font-medium text-text mb-1.5">QR Code Data</label>
        <textarea
          value={qrData} onChange={(e) => setQrData(e.target.value)}
          rows={4}
          className="w-full bg-white border border-border rounded-md py-2.5 px-3 text-text text-sm placeholder-text-muted/60 focus:outline-none focus:border-primary font-mono resize-none"
          placeholder='{"ticket_id": "...", ...}'
        />
        <button
          type="submit" disabled={loading || !qrData.trim()}
          className="mt-3 w-full inline-flex items-center justify-center gap-2 bg-primary hover:bg-primary-dark disabled:opacity-50 text-white font-medium py-2.5 rounded-md transition-colors cursor-pointer border-none text-sm"
        >
          <ScanLine className="w-4 h-4" />
          {loading ? 'Validating...' : 'Validate'}
        </button>
      </form>

      {result && (
        <div className={`rounded-lg border p-4 ${isValid ? 'bg-emerald-50 border-emerald-200' : isUsed ? 'bg-amber-50 border-amber-200' : 'bg-red-50 border-red-200'}`}>
          <div className="flex items-center gap-2.5 mb-2">
            {isValid ? (
              <CheckCircle className="w-5 h-5 text-success" />
            ) : isUsed ? (
              <AlertCircle className="w-5 h-5 text-amber-600" />
            ) : (
              <XCircle className="w-5 h-5 text-danger" />
            )}
            <div>
              <h3 className={`text-sm font-semibold ${isValid ? 'text-success' : isUsed ? 'text-amber-700' : 'text-danger'}`}>
                {isValid ? 'Valid - Allow Entry' : result.error_code || 'Invalid'}
              </h3>
              <p className="text-xs text-text-muted">{result.message || ''}</p>
            </div>
          </div>
          {result.ticket && (
            <div className="space-y-1.5 text-xs border-t border-black/5 pt-3 mt-2">
              <div className="flex justify-between"><span className="text-text-muted">Ticket</span><span className="font-mono">{result.ticket.ticket_id?.slice(0, 16)}...</span></div>
              {result.ticket.event_name && <div className="flex justify-between"><span className="text-text-muted">Event</span><span>{result.ticket.event_name}</span></div>}
              <div className="flex justify-between"><span className="text-text-muted">Status</span><span className="font-medium">{result.ticket.status}</span></div>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 bg-red-50 text-danger px-3 py-2.5 rounded-md text-sm border border-red-100">
          <AlertCircle className="w-4 h-4 shrink-0" /> {error}
        </div>
      )}
    </div>
  );
}
