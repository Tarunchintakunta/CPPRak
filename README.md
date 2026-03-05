# Rakshan - QR Ticket Management System

A secure event ticketing platform that uses cryptographically signed QR codes for tamper-proof ticket generation and validation.

## Architecture

```
Frontend (React + Vite + Tailwind)
       │
       ▼
Flask Backend (REST API)
  ├── DynamoDB (Users, Events, Registrations, Tickets)
  ├── S3 / Local Storage (QR code images)
  └── Lambda Functions
        ├── QR Generator (HMAC-SHA256 signed tickets)
        └── QR Validator (signature + status verification)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, Tailwind CSS, React Router, Axios |
| Backend | Flask, Flask-CORS |
| Database | AWS DynamoDB (local for dev) |
| Auth | JWT (PyJWT), bcrypt |
| QR System | qrcode (Python), HMAC-SHA256 signatures |
| Storage | AWS S3 / local filesystem |
| Serverless | AWS Lambda (local invocation for dev) |

## Project Structure

```
├── frontend/             # React SPA
│   └── src/
│       ├── pages/        # Home, Login, Register, Events, Tickets, Admin
│       ├── components/   # Navbar, ProtectedRoute, LoadingSpinner
│       ├── context/      # AuthContext (JWT + user state)
│       └── services/     # API client (axios)
├── backend/              # Flask REST API
│   └── app/
│       ├── routes/       # auth, events, registrations, tickets, admin
│       ├── services/     # dynamo, s3, lambda, auth services
│       ├── middleware/   # JWT auth decorators
│       └── models/       # DynamoDB table schemas
├── qr_ticket_manager/   # Standalone Python library
│   └── qr_ticket_manager/
│       ├── ticket_generator.py   # HMAC-SHA256 ticket creation
│       ├── qr_code_creator.py    # QR image generation
│       └── ticket_validator.py   # Two-layer validation
├── lambda_functions/     # Serverless handlers
│   ├── qr_generator/    # Generate ticket + QR code
│   └── qr_validator/    # Validate scanned QR data
└── infrastructure/       # AWS IaC (placeholder)
```

## Setup

### Prerequisites

- Python 3.9+
- Node.js 18+
- DynamoDB Local (or AWS account)

### Backend

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
pip install -e qr_ticket_manager/

# Start DynamoDB Local (Docker)
docker run -p 8000:8000 amazon/dynamodb-local

# Run the Flask server
python backend/run.py
```

The API runs on `http://localhost:5000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app runs on `http://localhost:3000` with API proxy to the backend.

## API Endpoints

### Auth
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | - | Register new user |
| POST | `/api/auth/login` | - | Login, get JWT |
| GET | `/api/auth/me` | Token | Get current user |

### Events
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/events/` | - | List active events |
| GET | `/api/events/:id` | - | Get event details |
| POST | `/api/events/` | Admin | Create event |
| PUT | `/api/events/:id` | Admin | Update event |
| DELETE | `/api/events/:id` | Admin | Delete event |

### Registrations
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/registrations/` | Token | Register for event |
| GET | `/api/registrations/` | Token | List my registrations |
| GET | `/api/registrations/:id` | Token | Get registration |
| DELETE | `/api/registrations/:id` | Token | Cancel registration |

### Tickets
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/tickets/:id` | Token | Get ticket details |
| GET | `/api/tickets/:id/qr` | - | Get QR code image |
| POST | `/api/tickets/validate` | - | Validate QR data |

### Admin
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/admin/dashboard` | Admin | Dashboard stats |
| GET | `/api/admin/events/:id/attendees` | Admin | Event attendees |
| GET | `/api/admin/events/:id/export` | Admin | Export CSV |

## Features

- **User auth** with JWT tokens and bcrypt password hashing
- **Event management** with capacity control and status tracking
- **QR ticket generation** using HMAC-SHA256 cryptographic signatures
- **Two-layer ticket validation** (signature integrity + database status)
- **Check-in system** marking tickets as used and registrations as checked-in
- **Admin dashboard** with aggregate stats, attendee lists, and CSV export
- **Dual-mode** operation: local development and AWS production
