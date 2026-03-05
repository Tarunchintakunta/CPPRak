# Rakshan - Secure QR Ticket Management System

A cloud-based event ticketing platform that uses HMAC-SHA256 cryptographically signed QR codes for tamper-proof ticket generation and validation. Built with Flask, React, and deployed on AWS using DynamoDB, S3, Lambda, Elastic Beanstalk, and IAM.

## Deployed Application

- **Frontend**: http://rakshan-frontend.s3-website-ap-southeast-2.amazonaws.com
- **Backend API**: http://rakshan-prod.eba-7mxtcx4w.ap-southeast-2.elasticbeanstalk.com
- **Health Check**: http://rakshan-prod.eba-7mxtcx4w.ap-southeast-2.elasticbeanstalk.com/api/health

### Demo Credentials

| Role  | Email              | Password  |
|-------|--------------------|-----------|
| Admin | admin@rakshan.com  | admin123  |
| User  | (register via UI)  | -         |

---

## Architecture

```
                    ┌─────────────────────────────────────┐
                    │        Frontend (React SPA)          │
                    │   S3 Static Website Hosting           │
                    │   rakshan-frontend.s3-website-...     │
                    └──────────────┬──────────────────────┘
                                   │ HTTP API calls
                                   ▼
                    ┌─────────────────────────────────────┐
                    │     Backend (Flask REST API)          │
                    │   Elastic Beanstalk (Python 3.9)      │
                    │   rakshan-prod.eba-...                 │
                    └──┬──────┬──────────┬───────────────┘
                       │      │          │
              ┌────────┘      │          └────────┐
              ▼               ▼                   ▼
     ┌────────────┐  ┌──────────────┐   ┌──────────────┐
     │  DynamoDB   │  │   S3 Bucket   │   │   Lambda     │
     │  4 Tables:  │  │ rakshan-qr-   │   │ Functions    │
     │  - Users    │  │ tickets       │   │              │
     │  - Events   │  │ (QR images)   │   │ - generator  │
     │  - Tickets  │  │               │   │ - validator  │
     │  - Regs     │  └──────────────┘   └──────────────┘
     └────────────┘
                       │
              ┌────────┘
              ▼
     ┌────────────────┐
     │  IAM Roles      │
     │  - EB EC2 role  │
     │  - Lambda role  │
     └────────────────┘
```

### AWS Cloud Services Used (5 services)

| # | Service | Purpose |
|---|---------|---------|
| 1 | **Amazon DynamoDB** | NoSQL database for Users, Events, Registrations, and Tickets tables with GSIs for query patterns |
| 2 | **Amazon S3** | Static website hosting for the React frontend; object storage for QR code PNG images |
| 3 | **AWS Lambda** | Serverless QR ticket generation (HMAC signing + image creation) and QR ticket validation |
| 4 | **AWS Elastic Beanstalk** | Managed deployment of the Flask backend on EC2 with auto-provisioned security groups |
| 5 | **AWS IAM** | Role-based access control for EC2 instances and Lambda functions with least-privilege policies |

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Frontend | React, Vite, Tailwind CSS v4, React Router, Axios | React 19, Vite 7 |
| Backend | Flask, Flask-CORS, Gunicorn | Flask 3.x |
| Database | Amazon DynamoDB (provisioned mode, 5 RCU/WCU) | - |
| Auth | JWT (PyJWT) + bcrypt password hashing | - |
| QR System | qr_ticket_manager (custom library), qrcode, Pillow | 1.0.0 |
| Storage | Amazon S3 (QR images + frontend hosting) | - |
| Serverless | AWS Lambda (Python 3.9 runtime) | - |
| Hosting | AWS Elastic Beanstalk (Python 3.9 on Amazon Linux 2023) | - |
| Version Control | Git + GitHub (private repository) | - |

---

## Project Structure

```
rakshan/
├── frontend/                    # React single-page application
│   ├── src/
│   │   ├── pages/               # Home, Login, Register, Events, EventDetail,
│   │   │                        # MyTickets, TicketDetail, AdminDashboard,
│   │   │                        # CreateEvent, ScanTicket
│   │   ├── components/common/   # Navbar, ProtectedRoute, LoadingSpinner
│   │   ├── context/             # AuthContext (JWT token + user state management)
│   │   └── services/            # api.js (Axios HTTP client)
│   ├── vite.config.js           # Vite config with dev proxy and Tailwind plugin
│   └── package.json
│
├── backend/                     # Flask REST API
│   ├── app/
│   │   ├── __init__.py          # Application factory (create_app)
│   │   ├── config.py            # DevelopmentConfig / ProductionConfig
│   │   ├── routes/              # auth, events, registrations, tickets, admin
│   │   ├── services/            # dynamo_service, s3_service, lambda_service, auth_service
│   │   ├── middleware/          # JWT auth decorators (token_required, admin_required)
│   │   └── models/              # DynamoDB table schemas with GSI definitions
│   ├── qr_ticket_manager/      # Library copy for EB deployment
│   ├── application.py           # EB entry point (Gunicorn WSGI)
│   ├── Procfile                 # Gunicorn process config
│   ├── .ebextensions/           # EB environment configuration
│   │   └── 01_flask.config      # Environment variables and WSGI path
│   └── requirements.txt
│
├── qr_ticket_manager/           # Custom Python library (standalone package)
│   ├── qr_ticket_manager/
│   │   ├── __init__.py          # Public API exports
│   │   ├── ticket_generator.py  # HMAC-SHA256 ticket creation and signing
│   │   ├── ticket_validator.py  # Two-layer validation (signature + status)
│   │   ├── qr_code_creator.py   # QR code image generation (PNG, base64, file)
│   │   ├── exceptions.py        # Custom exception hierarchy (9 exception classes)
│   │   └── logger.py            # CloudWatch-compatible structured JSON logging
│   ├── tests/                   # 15 unit tests (pytest)
│   │   ├── test_ticket_generator.py
│   │   ├── test_ticket_validator.py
│   │   └── test_qr_code_creator.py
│   ├── pyproject.toml           # Package metadata and build config
│   └── setup.py
│
├── lambda_functions/            # AWS Lambda handlers
│   ├── qr_generator/
│   │   └── handler.py           # Generates ticket, creates QR, stores in S3 + DynamoDB
│   └── qr_validator/
│       └── handler.py           # Validates QR data, marks ticket used, updates registration
│
└── infrastructure/              # AWS infrastructure (managed via CLI)
```

---

## Dependencies

### Backend (Python 3.9+)

```
flask              # Web framework
flask-cors         # Cross-origin resource sharing
boto3              # AWS SDK for Python (DynamoDB, S3, Lambda)
pyjwt              # JSON Web Token encoding/decoding
bcrypt             # Password hashing
qrcode             # QR code generation
pillow             # Image processing for QR codes
gunicorn           # Production WSGI server
pytest             # Testing framework
requests           # HTTP client
```

### Frontend (Node.js 18+)

```
react              # UI framework (v19)
react-dom          # React DOM renderer
react-router-dom   # Client-side routing
axios              # HTTP client for API calls
lucide-react       # Icon library
@tailwindcss/vite  # Tailwind CSS v4 Vite plugin
vite               # Build tool and dev server
```

### Custom Library

```
qr_ticket_manager  # v1.0.0 — HMAC-SHA256 ticket signing and validation
                   # Dependencies: qrcode>=7.0, Pillow>=9.0
```

---

## Local Development Setup

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Docker (for DynamoDB Local)
- AWS CLI v2 (for production deployment)

### Step 1: Clone the repository

```bash
git clone https://github.com/Tarunchintakunta/CPPRak.git
cd CPPRak
```

### Step 2: Start DynamoDB Local

```bash
docker run -d -p 8000:8000 amazon/dynamodb-local
```

### Step 3: Backend setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Install the custom QR ticket library in editable mode
pip install -e qr_ticket_manager/

# Start the Flask development server
python backend/run.py
```

The API server starts on `http://localhost:5000`. DynamoDB tables are created automatically on startup.

### Step 4: Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The React app starts on `http://localhost:3000`. The Vite dev server proxies `/api` requests to the Flask backend.

### Step 5: Run library tests

```bash
cd qr_ticket_manager
pytest tests/ -v
```

All 15 tests should pass covering ticket generation, validation, and QR code creation.

---

## AWS Deployment Steps

### Prerequisites

- AWS CLI v2 configured with IAM credentials
- EB CLI (`pip install awsebcli`)

### Step 1: Configure AWS CLI

```bash
aws configure
# Region: ap-southeast-2
# Output: json
```

### Step 2: Create DynamoDB tables

```bash
# Users table with email GSI
aws dynamodb create-table --table-name Users \
  --key-schema AttributeName=user_id,KeyType=HASH \
  --attribute-definitions AttributeName=user_id,AttributeType=S AttributeName=email,AttributeType=S \
  --global-secondary-indexes '[{"IndexName":"email-index","KeySchema":[{"AttributeName":"email","KeyType":"HASH"}],"Projection":{"ProjectionType":"ALL"},"ProvisionedThroughput":{"ReadCapacityUnits":5,"WriteCapacityUnits":5}}]' \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Events table with status-date GSI
aws dynamodb create-table --table-name Events \
  --key-schema AttributeName=event_id,KeyType=HASH \
  --attribute-definitions AttributeName=event_id,AttributeType=S AttributeName=status,AttributeType=S AttributeName=date,AttributeType=S \
  --global-secondary-indexes '[{"IndexName":"status-date-index","KeySchema":[{"AttributeName":"status","KeyType":"HASH"},{"AttributeName":"date","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"},"ProvisionedThroughput":{"ReadCapacityUnits":5,"WriteCapacityUnits":5}}]' \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Registrations table with user-event and event GSIs
aws dynamodb create-table --table-name Registrations \
  --key-schema AttributeName=registration_id,KeyType=HASH \
  --attribute-definitions AttributeName=registration_id,AttributeType=S AttributeName=user_id,AttributeType=S AttributeName=event_id,AttributeType=S \
  --global-secondary-indexes '[{"IndexName":"user-event-index","KeySchema":[{"AttributeName":"user_id","KeyType":"HASH"},{"AttributeName":"event_id","KeyType":"RANGE"}],"Projection":{"ProjectionType":"ALL"},"ProvisionedThroughput":{"ReadCapacityUnits":5,"WriteCapacityUnits":5}},{"IndexName":"event-index","KeySchema":[{"AttributeName":"event_id","KeyType":"HASH"}],"Projection":{"ProjectionType":"ALL"},"ProvisionedThroughput":{"ReadCapacityUnits":5,"WriteCapacityUnits":5}}]' \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5

# Tickets table with registration GSI
aws dynamodb create-table --table-name Tickets \
  --key-schema AttributeName=ticket_id,KeyType=HASH \
  --attribute-definitions AttributeName=ticket_id,AttributeType=S AttributeName=registration_id,AttributeType=S \
  --global-secondary-indexes '[{"IndexName":"registration-index","KeySchema":[{"AttributeName":"registration_id","KeyType":"HASH"}],"Projection":{"ProjectionType":"ALL"},"ProvisionedThroughput":{"ReadCapacityUnits":5,"WriteCapacityUnits":5}}]' \
  --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5
```

### Step 3: Create S3 buckets

```bash
# QR code image storage bucket
aws s3 mb s3://rakshan-qr-tickets

# Frontend static hosting bucket
aws s3 mb s3://rakshan-frontend
aws s3 website s3://rakshan-frontend --index-document index.html --error-document index.html

# Allow public read access for frontend
aws s3api put-public-access-block --bucket rakshan-frontend \
  --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

aws s3api put-bucket-policy --bucket rakshan-frontend --policy '{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::rakshan-frontend/*"
  }]
}'
```

### Step 4: Create IAM role and deploy Lambda functions

```bash
# Create Lambda execution role
aws iam create-role --role-name rakshan-lambda-role \
  --assume-role-policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

# Attach policies
aws iam attach-role-policy --role-name rakshan-lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam attach-role-policy --role-name rakshan-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam attach-role-policy --role-name rakshan-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess

# Package and deploy QR Generator Lambda
cd /tmp && mkdir -p lambda_gen && cd lambda_gen
cp <project_root>/lambda_functions/qr_generator/handler.py .
cp -r <project_root>/qr_ticket_manager/qr_ticket_manager/ .
pip install qrcode pillow -t .
zip -r /tmp/qr_generator.zip .

aws lambda create-function --function-name qr-ticket-generator \
  --runtime python3.9 --role <LAMBDA_ROLE_ARN> \
  --handler handler.handler --zip-file fileb:///tmp/qr_generator.zip \
  --timeout 30 --memory-size 256 \
  --environment "Variables={TICKET_SECRET_KEY=ticket-hmac-secret-key-2026,S3_BUCKET=rakshan-qr-tickets}"

# Package and deploy QR Validator Lambda
cd /tmp && mkdir -p lambda_val && cd lambda_val
cp <project_root>/lambda_functions/qr_validator/handler.py .
cp -r <project_root>/qr_ticket_manager/qr_ticket_manager/ .
zip -r /tmp/qr_validator.zip .

aws lambda create-function --function-name qr-ticket-validator \
  --runtime python3.9 --role <LAMBDA_ROLE_ARN> \
  --handler handler.handler --zip-file fileb:///tmp/qr_validator.zip \
  --timeout 30 --memory-size 128 \
  --environment "Variables={TICKET_SECRET_KEY=ticket-hmac-secret-key-2026}"
```

### Step 5: Deploy backend to Elastic Beanstalk

```bash
cd backend

# Initialise EB application
eb init rakshan-backend --platform python-3.9 --region ap-southeast-2

# Create environment (single instance, t3.micro)
eb create rakshan-prod --single --instance-types t3.micro

# Attach DynamoDB/S3/Lambda permissions to the EB EC2 role
aws iam attach-role-policy --role-name aws-elasticbeanstalk-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess
aws iam attach-role-policy --role-name aws-elasticbeanstalk-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
aws iam attach-role-policy --role-name aws-elasticbeanstalk-ec2-role \
  --policy-arn arn:aws:iam::aws:policy/AWSLambda_FullAccess

# Restart to pick up new permissions
aws elasticbeanstalk restart-app-server --environment-name rakshan-prod
```

### Step 6: Build and deploy frontend

```bash
cd frontend

# Build with production API URL
VITE_API_URL=http://<EB_CNAME>/api npm run build

# Upload to S3
aws s3 sync dist/ s3://rakshan-frontend/ --delete
```

---

## Configuration Files

### backend/.ebextensions/01_flask.config

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
    TICKET_SECRET_KEY: ticket-hmac-secret-key-2026
    S3_BUCKET: rakshan-qr-tickets
    AWS_REGION: ap-southeast-2
  aws:elasticbeanstalk:container:python:
    WSGIPath: application:application
```

### backend/Procfile

```
web: gunicorn application:application --bind 0.0.0.0:8000
```

### backend/app/config.py

The application uses two configuration classes:

- `DevelopmentConfig` — uses DynamoDB Local (port 8000), local filesystem storage, local Lambda invocation
- `ProductionConfig` — uses AWS DynamoDB, S3, and Lambda services with IAM role-based auth

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | `development` or `production` | `development` |
| `SECRET_KEY` | JWT signing secret | `dev-secret-key-change-in-production` |
| `TICKET_SECRET_KEY` | HMAC-SHA256 key for ticket signing | `ticket-hmac-secret-key-2026` |
| `S3_BUCKET` | S3 bucket name for QR images | `rakshan-qr-tickets` |
| `AWS_REGION` | AWS region | `ap-southeast-2` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000` |
| `VITE_API_URL` | Backend API base URL (frontend build-time) | `/api` |

---

## API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | None | Register new user (name, email, password) |
| POST | `/api/auth/login` | None | Login, returns JWT token |
| GET | `/api/auth/me` | JWT | Get current user profile |

### Events (CRUD)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/events/` | None | List active events (filterable by status) |
| GET | `/api/events/:id` | None | Get single event details |
| POST | `/api/events/` | Admin | Create new event |
| PUT | `/api/events/:id` | Admin | Update event |
| DELETE | `/api/events/:id` | Admin | Delete event |

### Registrations
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/registrations/` | JWT | Register for event (validates capacity, duplicates) |
| GET | `/api/registrations/` | JWT | List user's registrations with event details |
| GET | `/api/registrations/:id` | JWT | Get single registration with ticket info |
| DELETE | `/api/registrations/:id` | JWT | Cancel registration and revoke ticket |

### Tickets
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/tickets/:id` | JWT | Get ticket details with QR URL |
| GET | `/api/tickets/:id/qr` | None | Serve QR code image (PNG) |
| POST | `/api/tickets/validate` | None | Validate scanned QR data via Lambda |

### Admin
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/admin/dashboard` | Admin | Aggregate stats (users, events, tickets) |
| GET | `/api/admin/events/:id/attendees` | Admin | Attendee list with check-in status |
| GET | `/api/admin/events/:id/export` | Admin | Export attendees as CSV |

---

## Custom Library: qr_ticket_manager

### Purpose

The `qr_ticket_manager` library provides the core cryptographic ticketing functionality. It generates HMAC-SHA256 signed ticket identifiers, creates QR code images encoding the signed payload, and validates scanned QR codes through a two-layer verification process (cryptographic signature integrity check followed by database status verification).

### Classes

| Class | Description |
|-------|-------------|
| `TicketGenerator` | Creates ticket IDs, signs payloads with HMAC-SHA256, produces QR-encodable JSON |
| `TicketValidator` | Verifies HMAC signatures and checks ticket status (valid/used/revoked/expired) |
| `QRCodeCreator` | Generates QR code images as PNG bytes, base64 strings, or saved files |
| `TicketLogger` | Structured JSON logging compatible with AWS CloudWatch Logs |

### Exception Hierarchy

```
QRTicketError (base)
├── TicketGenerationError
├── TicketValidationError
│   ├── InvalidSignatureError
│   ├── TicketAlreadyUsedError
│   ├── TicketRevokedError
│   └── TicketExpiredError
├── QRCodeGenerationError
└── StorageError
```

### Tests

15 unit tests covering:
- Unique ticket ID generation
- HMAC-SHA256 signature determinism and key sensitivity
- Ticket payload structure and QR payload JSON validity
- Signature verification (valid and tampered payloads)
- Status checking (valid, used, revoked)
- Full validation pipeline
- QR code image generation (PNG bytes, base64, file save)
- Error cases (empty keys, missing fields, empty data)

---

## Features

- **JWT Authentication** — Token-based auth with bcrypt password hashing and role-based access (user/admin)
- **Event Management** — Full CRUD with capacity control, status tracking, and date-based querying via DynamoDB GSIs
- **QR Ticket Generation** — HMAC-SHA256 cryptographic signing ensures tickets cannot be forged or tampered with
- **Two-Layer Validation** — Layer 1: signature integrity verification; Layer 2: database status check (prevents reuse)
- **Check-In System** — Scanning marks tickets as used and registrations as checked-in with timestamps
- **Admin Dashboard** — Aggregate statistics, per-event attendee lists, and CSV export functionality
- **Dual-Mode Operation** — Development mode uses DynamoDB Local + local filesystem; production uses AWS services
- **Serverless Processing** — Lambda functions handle QR generation and validation independently of the web server
- **Structured Logging** — CloudWatch-compatible JSON logging throughout the library and Lambda handlers

---

## DynamoDB Table Design

### Users
- **PK**: `user_id` (String)
- **GSI**: `email-index` (email → all attributes)

### Events
- **PK**: `event_id` (String)
- **GSI**: `status-date-index` (status + date range for querying active events chronologically)

### Registrations
- **PK**: `registration_id` (String)
- **GSI**: `user-event-index` (user_id + event_id for duplicate checks and user queries)
- **GSI**: `event-index` (event_id for attendee listing)

### Tickets
- **PK**: `ticket_id` (String)
- **GSI**: `registration-index` (registration_id for ticket lookup by registration)
