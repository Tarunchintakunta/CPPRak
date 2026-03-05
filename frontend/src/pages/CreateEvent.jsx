import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import { ArrowLeft, AlertCircle, CheckCircle } from 'lucide-react';

export default function CreateEvent() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', description: '', date: '', time: '', location: '', capacity: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await eventsAPI.create({ ...form, capacity: parseInt(form.capacity) });
      navigate('/admin');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create event');
    } finally {
      setLoading(false);
    }
  };

  const fields = [
    { name: 'name', label: 'Event Name', type: 'text', placeholder: 'e.g. Tech Summit 2026', required: true },
    { name: 'description', label: 'Description', type: 'textarea', placeholder: 'Describe the event...', required: false },
    { name: 'date', label: 'Date', type: 'date', required: true },
    { name: 'time', label: 'Time', type: 'time', required: true },
    { name: 'location', label: 'Location', type: 'text', placeholder: 'e.g. Convention Center, Hall A', required: true },
    { name: 'capacity', label: 'Capacity', type: 'number', placeholder: 'e.g. 500', required: true },
  ];

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-10">
      <button onClick={() => navigate('/admin')} className="flex items-center gap-1.5 text-text-muted hover:text-text text-sm mb-6 bg-transparent border-none cursor-pointer font-medium">
        <ArrowLeft className="w-4 h-4" /> Back to dashboard
      </button>

      <h1 className="text-3xl font-bold mb-8">Create Event</h1>

      <form onSubmit={handleSubmit} className="bg-surface rounded-2xl border border-surface-lighter p-8">
        {error && (
          <div className="flex items-center gap-2 bg-danger/10 text-danger px-4 py-3 rounded-lg mb-6 text-sm">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        <div className="space-y-5">
          {fields.map(({ name, label, type, placeholder, required }) => (
            <div key={name}>
              <label className="block text-sm font-medium text-text-muted mb-2">{label}{required && <span className="text-danger ml-0.5">*</span>}</label>
              {type === 'textarea' ? (
                <textarea
                  name={name} value={form[name]} onChange={handleChange} rows={3} placeholder={placeholder}
                  className="w-full bg-surface-light border border-surface-lighter rounded-lg py-3 px-4 text-text placeholder-text-muted/50 focus:outline-none focus:border-primary text-sm resize-none"
                />
              ) : (
                <input
                  type={type} name={name} value={form[name]} onChange={handleChange} required={required} placeholder={placeholder}
                  className="w-full bg-surface-light border border-surface-lighter rounded-lg py-3 px-4 text-text placeholder-text-muted/50 focus:outline-none focus:border-primary text-sm"
                />
              )}
            </div>
          ))}
        </div>

        <button
          type="submit" disabled={loading}
          className="mt-8 w-full inline-flex items-center justify-center gap-2 bg-primary hover:bg-primary-dark disabled:opacity-50 text-white font-semibold py-3.5 rounded-xl transition-colors cursor-pointer border-none text-base"
        >
          <CheckCircle className="w-5 h-5" />
          {loading ? 'Creating...' : 'Create Event'}
        </button>
      </form>
    </div>
  );
}
