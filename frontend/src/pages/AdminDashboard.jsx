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
    { label: 'Total Users', value: stats?.total_users || 0, icon: Users, color: 'text-primary' },
    { label: 'Active Events', value: stats?.active_events || 0, icon: Calendar, color: 'text-success' },
    { label: 'Registrations', value: stats?.confirmed_registrations || 0, icon: CheckCircle, color: 'text-secondary' },
    { label: 'Total Tickets', value: stats?.total_tickets || 0, icon: Ticket, color: 'text-accent' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <h1 className="text-3xl font-bold">Admin Dashboard</h1>
        <div className="flex items-center gap-3">
          <Link to="/admin/scan" className="inline-flex items-center gap-1.5 bg-surface-light hover:bg-surface-lighter text-text px-4 py-2.5 rounded-lg text-sm font-medium no-underline border border-surface-lighter transition-colors">
            <ScanLine className="w-4 h-4" /> Scan Ticket
          </Link>
          <Link to="/admin/create-event" className="inline-flex items-center gap-1.5 bg-primary hover:bg-primary-dark text-white px-4 py-2.5 rounded-lg text-sm font-medium no-underline transition-colors">
            <Plus className="w-4 h-4" /> Create Event
          </Link>
        </div>
      </div>

      {/* Stats */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-surface rounded-xl border border-surface-lighter p-5">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-text-muted">{label}</span>
              <Icon className={`w-5 h-5 ${color}`} />
            </div>
            <p className="text-3xl font-bold">{value}</p>
          </div>
        ))}
      </div>

      {/* Events list */}
      <h2 className="text-xl font-semibold mb-4">Events</h2>
      <div className="bg-surface rounded-xl border border-surface-lighter overflow-hidden mb-8">
        {events.length === 0 ? (
          <p className="text-text-muted text-center py-8">No events yet</p>
        ) : (
          <div className="divide-y divide-surface-lighter">
            {events.map((event) => (
              <div key={event.event_id} className="flex items-center justify-between p-4 hover:bg-surface-light transition-colors">
                <div className="min-w-0 flex-1">
                  <h3 className="font-medium truncate">{event.name}</h3>
                  <p className="text-sm text-text-muted">{event.date} &middot; {event.location} &middot; Cap: {event.capacity}</p>
                </div>
                <div className="flex items-center gap-2 shrink-0 ml-4">
                  <a
                    href={adminAPI.exportUrl(event.event_id)}
                    className="inline-flex items-center gap-1 text-xs text-text-muted hover:text-text bg-surface-lighter px-3 py-1.5 rounded-lg no-underline transition-colors"
                    target="_blank" rel="noopener noreferrer"
                  >
                    <Download className="w-3.5 h-3.5" /> CSV
                  </a>
                  <button
                    onClick={() => viewAttendees(event.event_id)}
                    className="inline-flex items-center gap-1 text-xs bg-primary/15 text-primary hover:bg-primary/25 px-3 py-1.5 rounded-lg border-none cursor-pointer font-medium transition-colors"
                  >
                    Attendees <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Attendee list */}
      {selectedEvent && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">
              Attendees
              <span className="text-text-muted font-normal text-base ml-2">({attendees.length})</span>
            </h2>
            <button onClick={() => setSelectedEvent(null)} className="text-sm text-text-muted hover:text-text bg-transparent border-none cursor-pointer">
              Close
            </button>
          </div>

          {loadingAttendees ? (
            <LoadingSpinner size="sm" />
          ) : attendees.length === 0 ? (
            <p className="text-text-muted text-center py-8 bg-surface rounded-xl border border-surface-lighter">No attendees yet</p>
          ) : (
            <div className="bg-surface rounded-xl border border-surface-lighter overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-surface-lighter text-left">
                    <th className="px-4 py-3 font-medium text-text-muted">Name</th>
                    <th className="px-4 py-3 font-medium text-text-muted">Email</th>
                    <th className="px-4 py-3 font-medium text-text-muted">Status</th>
                    <th className="px-4 py-3 font-medium text-text-muted">Checked In</th>
                    <th className="px-4 py-3 font-medium text-text-muted">Ticket</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-lighter">
                  {attendees.map((a) => (
                    <tr key={a.registration_id} className="hover:bg-surface-light">
                      <td className="px-4 py-3 font-medium">{a.name || 'N/A'}</td>
                      <td className="px-4 py-3 text-text-muted">{a.email || 'N/A'}</td>
                      <td className="px-4 py-3">
                        <span className={`inline-flex items-center gap-1 text-xs font-medium ${a.status === 'confirmed' ? 'text-success' : 'text-danger'}`}>
                          {a.status === 'confirmed' ? <CheckCircle className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                          {a.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {a.checked_in ? (
                          <span className="inline-flex items-center gap-1 text-xs text-success"><UserCheck className="w-3 h-3" /> Yes</span>
                        ) : (
                          <span className="text-xs text-text-muted">No</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-xs font-medium ${a.ticket_status === 'valid' ? 'text-success' : a.ticket_status === 'used' ? 'text-accent' : 'text-danger'}`}>
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
