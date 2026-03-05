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
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <h1 className="text-3xl font-bold">Upcoming Events</h1>
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted" />
          <input
            type="text" value={search} onChange={(e) => setSearch(e.target.value)}
            placeholder="Search events..."
            className="w-full bg-surface border border-surface-lighter rounded-lg py-2.5 pl-10 pr-4 text-text placeholder-text-muted/50 focus:outline-none focus:border-primary text-sm"
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="text-center py-20">
          <Calendar className="w-16 h-16 text-text-muted/30 mx-auto mb-4" />
          <p className="text-text-muted text-lg">No events found</p>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((event) => (
            <Link
              key={event.event_id} to={`/events/${event.event_id}`}
              className="bg-surface rounded-2xl border border-surface-lighter hover:border-primary/40 p-6 no-underline text-text transition-all hover:-translate-y-0.5 group"
            >
              <div className="flex items-center gap-2 text-primary text-sm font-medium mb-3">
                <Calendar className="w-4 h-4" />
                {event.date}
                <span className="text-text-muted ml-1 flex items-center gap-1">
                  <Clock className="w-3.5 h-3.5" /> {event.time}
                </span>
              </div>
              <h3 className="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">{event.name}</h3>
              {event.description && (
                <p className="text-text-muted text-sm mb-4 line-clamp-2">{event.description}</p>
              )}
              <div className="flex items-center gap-4 text-sm text-text-muted">
                <span className="flex items-center gap-1"><MapPin className="w-4 h-4" /> {event.location}</span>
                <span className="flex items-center gap-1"><Users className="w-4 h-4" /> {event.capacity}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
