import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { authAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Mail, AlertCircle, CheckCircle } from 'lucide-react';

export default function VerifyEmail() {
  const [code, setCode] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, refreshUser } = useAuth();

  const email = location.state?.email || user?.email || '';

  useEffect(() => {
    if (!email) navigate('/register');
  }, [email, navigate]);

  const handleVerify = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      await authAPI.verifyEmail({ email, code });
      setSuccess('Email verified successfully!');
      if (refreshUser) await refreshUser();
      setTimeout(() => navigate('/events'), 1500);
    } catch (err) {
      setError(err.response?.data?.error || 'Verification failed');
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResending(true);
    setError('');
    try {
      await authAPI.resendCode({ email });
      setSuccess('New code sent to your email');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to resend code');
    } finally {
      setResending(false);
    }
  };

  return (
    <div className="flex-1 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="mb-8">
          <div className="w-10 h-10 bg-surface-alt rounded-lg flex items-center justify-center mb-4">
            <Mail className="w-5 h-5 text-accent" />
          </div>
          <h1 className="text-2xl font-bold text-text mb-1">Check your email</h1>
          <p className="text-text-muted text-sm">
            We sent a verification code to <span className="font-medium text-text">{email}</span>
          </p>
        </div>

        <form onSubmit={handleVerify}>
          {error && (
            <div className="flex items-center gap-2 bg-red-50 text-danger px-3 py-2.5 rounded-md mb-4 text-sm border border-red-100">
              <AlertCircle className="w-4 h-4 shrink-0" /> {error}
            </div>
          )}

          {success && (
            <div className="flex items-center gap-2 bg-emerald-50 text-success px-3 py-2.5 rounded-md mb-4 text-sm border border-emerald-100">
              <CheckCircle className="w-4 h-4 shrink-0" /> {success}
            </div>
          )}

          <div className="mb-5">
            <label className="block text-sm font-medium text-text mb-1.5">Verification code</label>
            <input
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              required
              maxLength={6}
              className="w-full bg-white border border-border rounded-md py-3 px-4 text-text text-center text-2xl tracking-[0.5em] font-mono placeholder-text-muted/40 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-colors"
              placeholder="000000"
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={loading || code.length < 6}
            className="w-full bg-primary hover:bg-primary-dark disabled:opacity-50 text-white font-medium py-2.5 rounded-md transition-colors cursor-pointer border-none text-sm"
          >
            {loading ? 'Verifying...' : 'Verify email'}
          </button>

          <div className="text-center mt-4">
            <button
              type="button"
              onClick={handleResend}
              disabled={resending}
              className="text-sm text-accent hover:text-accent-light bg-transparent border-none cursor-pointer font-medium disabled:opacity-50"
            >
              {resending ? 'Sending...' : "Didn't get the code? Resend"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
