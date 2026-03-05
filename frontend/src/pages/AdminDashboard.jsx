import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { adminAPI, eventsAPI } from '../services/api';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { Users, Calendar, Ticket, CheckCircle, ChevronRight, Download, UserCheck, XCircle, Plus, ScanLine } from 'lucide-react';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [attendees, setAttendees] = useState([]);
  const [loadingAttendees, setLoadingAttendees] = useState(false);

  useEffect(() => {
    Promise.all([
      adminAPI.dashboard(),
      eventsAPI.list(),
    ]).then(([dashRes, evRes]) => {
      setStats(dashRes.data.stats);
      setEvents(evRes.data.events || []);
    }).catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const viewAttendees = async (eventId) => {
    setSelectedEvent(eventId);
    setLoadingAttendees(true);
    try {
      const res = await adminAPI.attendees(eventId);
      setAttendees(res.data.attendees || []);
    } catch {
      setAttendees([]);
    } finally {
      setLoadingAttendees(false);
    }
  };

  if (loading) return <LoadingSpinner text="Loading dashboard..." />;

  const statCards = [
    { label: 'Users', value: stats?.total_users || 0, icon: Users },
    { label: 'Events', value: stats?.active_events || 0, icon: Calendar },
    { label: 'Registrations', value: stats?.confirmed_registrations || 0, icon: CheckCircle },
    { label: 'Tickets', value: stats?.total_tickets || 0, icon: Ticket },
  ];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className="flex items-center gap-2">
          <Link to="/admin/scan" className="inline-flex items-center gap-1.5 bg-white hover:bg-surface-alt text-text px-3 py-2 rounded-md text-xs font-medium no-underline border border-border transition-colors">
            <ScanLine className="w-3.5 h-3.5" /> Scan
          </Link>
          <Link to="/admin/create-event" className="inline-flex items-center gap-1.5 bg-primary hover:bg-primary-dark text-white px-3 py-2 rounded-md text-xs font-medium no-underline transition-colors">
            <Plus className="w-3.5 h-3.5" /> New Event
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-8">
        {statCards.map(({ label, value, icon: Icon }) => (
          <div key={label} className="bg-white rounded-lg border border-border-light p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs text-text-muted">{label}</span>
              <Icon className="w-4 h-4 text-text-muted" />
            </div>
            <p className="text-2xl font-bold text-text">{value}</p>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between mb-3">
        <h2 className="text-sm font-semibold text-text uppercase tracking-wide">Events</h2>
      </div>
      <div className="bg-white rounded-lg border border-border-light overflow-hidden mb-8">
        {events.length === 0 ? (
          <p className="text-text-muted text-center py-8 text-sm">No events yet</p>
        ) : (
          <div className="divide-y divide-border-light">
            {events.map((event) => (
              <div key={event.event_id} className="flex items-center justify-between p-3.5 hover:bg-surface-alt/50 transition-colors">
                <div className="min-w-0 flex-1">
                  <h3 className="text-sm font-medium truncate">{event.name}</h3>
                  <p className="text-xs text-text-muted">{event.date} &middot; {event.location} &middot; {event.capacity} cap</p>
                </div>
                <div className="flex items-center gap-1.5 shrink-0 ml-3">
                  <a
                    href={adminAPI.exportUrl(event.event_id)}
                    className="inline-flex items-center gap-1 text-[11px] text-text-muted hover:text-text bg-surface-alt px-2 py-1 rounded no-underline transition-colors border border-border-light"
                    target="_blank" rel="noopener noreferrer"
                  >
                    <Download className="w-3 h-3" /> CSV
                  </a>
                  <button
                    onClick={() => viewAttendees(event.event_id)}
                    className="inline-flex items-center gap-1 text-[11px] text-accent hover:text-accent-light bg-orange-50 px-2 py-1 rounded border border-orange-100 cursor-pointer font-medium transition-colors"
                  >
                    Attendees <ChevronRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedEvent && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-text uppercase tracking-wide">
              Attendees <span className="text-text-muted font-normal normal-case">({attendees.length})</span>
            </h2>
            <button onClick={() => setSelectedEvent(null)} className="text-xs text-text-muted hover:text-text bg-transparent border-none cursor-pointer">
              Close
            </button>
          </div>

          {loadingAttendees ? (
            <LoadingSpinner size="sm" />
          ) : attendees.length === 0 ? (
            <p className="text-text-muted text-center py-8 bg-white rounded-lg border border-border-light text-sm">No attendees yet</p>
          ) : (
            <div className="bg-white rounded-lg border border-border-light overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-border-light text-left">
                    <th className="px-3 py-2.5 font-medium text-text-muted text-xs">Name</th>
                    <th className="px-3 py-2.5 font-medium text-text-muted text-xs">Email</th>
                    <th className="px-3 py-2.5 font-medium text-text-muted text-xs">Status</th>
                    <th className="px-3 py-2.5 font-medium text-text-muted text-xs">Checked In</th>
                    <th className="px-3 py-2.5 font-medium text-text-muted text-xs">Ticket</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border-light">
                  {attendees.map((a) => (
                    <tr key={a.registration_id} className="hover:bg-surface-alt/50">
                      <td className="px-3 py-2.5 text-xs font-medium">{a.name || 'N/A'}</td>
                      <td className="px-3 py-2.5 text-xs text-text-muted">{a.email || 'N/A'}</td>
                      <td className="px-3 py-2.5">
                        <span className={`inline-flex items-center gap-1 text-[11px] font-medium ${a.status === 'confirmed' ? 'text-success' : 'text-danger'}`}>
                          {a.status === 'confirmed' ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                          {a.status}
                        </span>
                      </td>
                      <td className="px-3 py-2.5">
                        {a.checked_in ? (
                          <span className="inline-flex items-center gap-1 text-[11px] text-success"><UserCheck className="w-3 h-3" /> Yes</span>
                        ) : (
                          <span className="text-[11px] text-text-muted">No</span>
                        )}
                      </td>
                      <td className="px-3 py-2.5">
                        <span className={`text-[11px] font-medium ${a.ticket_status === 'valid' ? 'text-success' : a.ticket_status === 'used' ? 'text-amber-600' : 'text-danger'}`}>
                          {a.ticket_status || 'N/A'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
