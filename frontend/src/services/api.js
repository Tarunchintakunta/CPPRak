import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me'),
};

export const eventsAPI = {
  list: (status = 'active') => api.get(`/events/?status=${status}`),
  get: (id) => api.get(`/events/${id}`),
  create: (data) => api.post('/events/', data),
  update: (id, data) => api.put(`/events/${id}`, data),
  delete: (id) => api.delete(`/events/${id}`),
};

export const registrationsAPI = {
  create: (eventId) => api.post('/registrations/', { event_id: eventId }),
  list: () => api.get('/registrations/'),
  get: (id) => api.get(`/registrations/${id}`),
  cancel: (id) => api.delete(`/registrations/${id}`),
};

export const ticketsAPI = {
  get: (id) => api.get(`/tickets/${id}`),
  getQrUrl: (id) => `/api/tickets/${id}/qr`,
  validate: (qrData) => api.post('/tickets/validate', { qr_data: qrData }),
};

export const adminAPI = {
  dashboard: () => api.get('/admin/dashboard'),
  attendees: (eventId) => api.get(`/admin/events/${eventId}/attendees`),
  exportUrl: (eventId) => `/api/admin/events/${eventId}/export`,
};

export default api;
