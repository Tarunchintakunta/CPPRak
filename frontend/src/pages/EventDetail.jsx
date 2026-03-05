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
      <p className="text-text-muted">{error || 'Event not found'}</p>
    </div>
  );

  const details = [
    { icon: Calendar, label: 'Date', value: event.date },
    { icon: Clock, label: 'Time', value: event.time },
    { icon: MapPin, label: 'Location', value: event.location },
    { icon: Users, label: 'Capacity', value: `${event.capacity} attendees` },
  ];

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <button onClick={() => navigate('/events')} className="flex items-center gap-1.5 text-text-muted hover:text-text text-sm mb-6 bg-transparent border-none cursor-pointer font-medium">
        <ArrowLeft className="w-4 h-4" /> Events
      </button>

      <div className="bg-white rounded-lg border border-border-light p-6 sm:p-8">
        {event.status === 'active' && (
          <span className="inline-block text-xs font-medium text-success bg-emerald-50 border border-emerald-100 px-2 py-0.5 rounded mb-4">Active</span>
        )}

        <h1 className="text-2xl font-bold text-text mb-2">{event.name}</h1>

        {event.description && (
          <p className="text-text-mid text-sm leading-relaxed mb-6">{event.description}</p>
        )}

        <div className="grid sm:grid-cols-2 gap-3 mb-6">
          {details.map(({ icon: Icon, label, value }) => (
            <div key={label} className="flex items-center gap-3 py-2">
              <div className="w-8 h-8 rounded-md bg-surface-alt flex items-center justify-center shrink-0">
                <Icon className="w-4 h-4 text-text-mid" />
              </div>
              <div>
                <p className="text-[11px] text-text-muted uppercase tracking-wide">{label}</p>
                <p className="text-sm text-text font-medium">{value}</p>
              </div>
            </div>
          ))}
        </div>

        {message && (
          <div className="flex items-center gap-2 bg-emerald-50 text-success px-3 py-2.5 rounded-md mb-4 text-sm border border-emerald-100">
            <CheckCircle className="w-4 h-4 shrink-0" /> {message}
            <button onClick={() => navigate('/my-tickets')} className="ml-auto text-success underline bg-transparent border-none cursor-pointer text-sm">
              View tickets
            </button>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 bg-red-50 text-danger px-3 py-2.5 rounded-md mb-4 text-sm border border-red-100">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        {event.status === 'active' && !message && (
          <button
            onClick={handleRegister} disabled={registering}
            className="w-full bg-primary hover:bg-primary-dark disabled:opacity-50 text-white font-medium py-2.5 rounded-md transition-colors cursor-pointer border-none text-sm"
          >
            {registering ? 'Registering...' : user ? 'Register for this event' : 'Sign in to register'}
          </button>
        )}
      </div>
    </div>
  );
}
