import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { eventsAPI, registrationsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Calendar, Clock, MapPin, Users, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react';

export default function EventDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [registering, setRegistering] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    eventsAPI.get(id)
      .then((res) => setEvent(res.data.event))
      .catch(() => setError('Event not found'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleRegister = async () => {
    if (!user) { navigate('/login'); return; }
    setRegistering(true);
    setError('');
    setMessage(null);
    try {
      const res = await registrationsAPI.create(id);
      setMessage(res.data.message || 'Registered successfully!');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    } finally {
      setRegistering(false);
    }
  };

  if (loading) return <LoadingSpinner text="Loading event..." />;
  if (!event) return (
    <div className="max-w-3xl mx-auto px-4 py-20 text-center">
      <p className="text-text-muted text-lg">{error || 'Event not found'}</p>
    </div>
  );

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <button onClick={() => navigate('/events')} className="flex items-center gap-1.5 text-text-muted hover:text-text text-sm mb-6 bg-transparent border-none cursor-pointer font-medium">
        <ArrowLeft className="w-4 h-4" /> Back to events
      </button>

      <div className="bg-surface rounded-2xl border border-surface-lighter p-8">
        <div className="flex items-center gap-2 text-primary text-sm font-medium mb-4">
          <span className="px-3 py-1 bg-primary/15 rounded-full">
            {event.status === 'active' ? 'Active' : event.status}
          </span>
        </div>

        <h1 className="text-3xl font-bold mb-4">{event.name}</h1>

        {event.description && (
          <p className="text-text-muted leading-relaxed mb-6">{event.description}</p>
        )}

        <div className="grid sm:grid-cols-2 gap-4 mb-8">
          <div className="flex items-center gap-3 text-text-muted">
            <div className="w-10 h-10 bg-surface-light rounded-lg flex items-center justify-center">
              <Calendar className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="text-xs text-text-muted/70">Date</p>
              <p className="text-text font-medium">{event.date}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 text-text-muted">
            <div className="w-10 h-10 bg-surface-light rounded-lg flex items-center justify-center">
              <Clock className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="text-xs text-text-muted/70">Time</p>
              <p className="text-text font-medium">{event.time}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 text-text-muted">
            <div className="w-10 h-10 bg-surface-light rounded-lg flex items-center justify-center">
              <MapPin className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="text-xs text-text-muted/70">Location</p>
              <p className="text-text font-medium">{event.location}</p>
            </div>
          </div>
          <div className="flex items-center gap-3 text-text-muted">
            <div className="w-10 h-10 bg-surface-light rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="text-xs text-text-muted/70">Capacity</p>
              <p className="text-text font-medium">{event.capacity} attendees</p>
            </div>
          </div>
        </div>

        {message && (
          <div className="flex items-center gap-2 bg-success/10 text-success px-4 py-3 rounded-lg mb-4 text-sm">
            <CheckCircle className="w-4 h-4 shrink-0" /> {message}
            <button onClick={() => navigate('/my-tickets')} className="ml-auto text-success underline bg-transparent border-none cursor-pointer text-sm">
              View my tickets
            </button>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 bg-danger/10 text-danger px-4 py-3 rounded-lg mb-4 text-sm">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        {event.status === 'active' && !message && (
          <button
            onClick={handleRegister} disabled={registering}
            className="w-full bg-primary hover:bg-primary-dark disabled:opacity-50 text-white font-semibold py-3.5 rounded-xl transition-colors cursor-pointer border-none text-base"
          >
            {registering ? 'Registering...' : user ? 'Register for this event' : 'Sign in to register'}
          </button>
        )}
      </div>
    </div>
  );
}
