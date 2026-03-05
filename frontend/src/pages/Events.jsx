import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { eventsAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Calendar, MapPin, Users, Clock, Search } from 'lucide-react';

export default function Events() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    eventsAPI.list().then((res) => setEvents(res.data.events || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = events.filter((e) =>
    e.name?.toLowerCase().includes(search.toLowerCase()) ||
    e.location?.toLowerCase().includes(search.toLowerCase())
  );

  if (loading) return <LoadingSpinner text="Loading events..." />;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-text">Events</h1>
          <p className="text-sm text-text-muted mt-0.5">{filtered.length} upcoming</p>
        </div>
        <div className="relative w-full sm:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-muted" />
          <input
            type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search..."
            className="w-full bg-white border border-border rounded-md py-2 pl-9 pr-3 text-text text-sm placeholder-text-muted/60 focus:outline-none focus:border-primary"
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-20">
          <Calendar className="w-10 h-10 text-border mx-auto mb-3" />
          <p className="text-text-muted">No events found</p>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((event) => (
            <Link
              key={event.event_id} to={`/events/${event.event_id}`}
              className="bg-white rounded-lg border border-border-light hover:border-border p-5 no-underline text-text transition-all group"
            >
              <div className="flex items-center gap-2 text-xs text-text-muted mb-3">
                <Calendar className="w-3.5 h-3.5" />
                <span className="font-medium">{event.date}</span>
                <span className="flex items-center gap-0.5">
                  <Clock className="w-3 h-3" /> {event.time}
                </span>
              </div>
              <h3 className="text-base font-semibold mb-1.5 group-hover:text-accent transition-colors">{event.name}</h3>
              {event.description && (
                <p className="text-text-muted text-sm mb-3 line-clamp-2 leading-relaxed">{event.description}</p>
              )}
              <div className="flex items-center gap-3 text-xs text-text-muted pt-3 border-t border-border-light">
                <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {event.location}</span>
                <span className="flex items-center gap-1"><Users className="w-3 h-3" /> {event.capacity}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
