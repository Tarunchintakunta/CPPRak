import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import { ArrowLeft, AlertCircle } from 'lucide-react';

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
    { name: 'name', label: 'Event name', type: 'text', placeholder: 'Tech Summit 2026', required: true },
    { name: 'description', label: 'Description', type: 'textarea', placeholder: 'What is this event about?', required: false },
    { name: 'date', label: 'Date', type: 'date', required: true },
    { name: 'time', label: 'Time', type: 'time', required: true },
    { name: 'location', label: 'Location', type: 'text', placeholder: 'Convention Center, Hall A', required: true },
    { name: 'capacity', label: 'Capacity', type: 'number', placeholder: '500', required: true },
  ];

  const inputClass = "w-full bg-white border border-border rounded-md py-2.5 px-3 text-text text-sm placeholder-text-muted/60 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary/20 transition-colors";

  return (
    <div className="max-w-lg mx-auto px-4 sm:px-6 py-10">
      <button onClick={() => navigate('/admin')} className="flex items-center gap-1.5 text-text-muted hover:text-text text-sm mb-6 bg-transparent border-none cursor-pointer font-medium">
        <ArrowLeft className="w-4 h-4" /> Dashboard
      </button>

      <h1 className="text-2xl font-bold mb-6">Create Event</h1>

      <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-border-light p-6">
        {error && (
          <div className="flex items-center gap-2 bg-red-50 text-danger px-3 py-2.5 rounded-md mb-5 text-sm border border-red-100">
            <AlertCircle className="w-4 h-4 shrink-0" /> {error}
          </div>
        )}

        <div className="space-y-4">
          {fields.map(({ name, label, type, placeholder, required }) => (
            <div key={name}>
              <label className="block text-sm font-medium text-text mb-1.5">
                {label}{required && <span className="text-danger ml-0.5">*</span>}
              </label>
              {type === 'textarea' ? (
                <textarea
                  name={name} value={form[name]} onChange={handleChange} rows={3} placeholder={placeholder}
                  className={`${inputClass} resize-none`}
                />
              ) : (
                <input
                  type={type} name={name} value={form[name]} onChange={handleChange} required={required} placeholder={placeholder}
                  className={inputClass}
                />
              )}
            </div>
          ))}
        </div>

        <button
          type="submit" disabled={loading}
          className="mt-6 w-full bg-primary hover:bg-primary-dark disabled:opacity-50 text-white font-medium py-2.5 rounded-md transition-colors cursor-pointer border-none text-sm"
        >
          {loading ? 'Creating...' : 'Create event'}
        </button>
      </form>
    </div>
  );
}
