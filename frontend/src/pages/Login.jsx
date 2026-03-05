import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, AlertCircle } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/events');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-text mb-1">Welcome back</h1>
          <p className="text-text-muted text-sm">Sign in to your account</p>
        </div>

        <form onSubmit={handleSubmit}>
          {error && (
            <div className="flex items-center gap-2 bg-red-50 text-danger px-3 py-2.5 rounded-md mb-5 text-sm border border-red-100">
              <AlertCircle className="w-4 h-4 shrink-0" /> {error}
            </div>
          )}

          <div className="mb-4">
            <label className="block text-sm font-medium text-text mb-1.5">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                type="email" value={email} onChange={(e) => setEmail(e.target.value)} required
                className="w-full bg-white border border-border rounded-md py-2.5 pl-10 pr-3 text-text text-sm placeholder-text-muted/60 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-colors"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-text mb-1.5">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
              <input
                type="password" value={password} onChange={(e) => setPassword(e.target.value)} required
                className="w-full bg-white border border-border rounded-md py-2.5 pl-10 pr-3 text-text text-sm placeholder-text-muted/60 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-colors"
                placeholder="Enter your password"
              />
            </div>
          </div>

          <button
            type="submit" disabled={loading}
            className="w-full bg-primary hover:bg-primary-dark disabled:opacity-50 text-white font-medium py-2.5 rounded-md transition-colors cursor-pointer border-none text-sm"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>

          <p className="text-center text-text-muted text-sm mt-5">
            No account?{' '}
            <Link to="/register" className="text-accent hover:text-accent-light no-underline font-medium">Sign up</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
