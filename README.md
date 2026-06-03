# RemotePay

A production-grade fintech payment processing platform integrated with PayGate (South Africa).

## Overview

RemotePay is a self-hosted, cloud-agnostic payment gateway that enables merchants to accept payments securely. Built with:

- **Backend**: FastAPI (Python)
- **Frontend**: Next.js + Tailwind CSS
- **Database**: PostgreSQL
- **Payments**: PayGate integration (PayWeb, PaySubs)
- **Infrastructure**: Docker + Docker Compose
- **CI/CD**: GitHub Actions

## Features

### Core Functionality
- ✅ Payment initiation and processing
- ✅ Subscription management
- ✅ Webhook handling with signature verification
- ✅ Transaction reconciliation
- ✅ 3D Secure support
- ✅ QR code payments
- ✅ Payment links

### Security
- ✅ JWT authentication with RBAC
- ✅ Rate limiting
- ✅ CORS protection
- ✅ Input validation
- ✅ PCI DSS aligned (no card storage)
- ✅ Webhook signature verification
- ✅ Helmet.js security headers

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Development

```bash
# Clone repository
git clone https://github.com/HloniHypnotiseMe/RemotePay-.git
cd RemotePay-

# Start all services
docker-compose up -d

# Backend runs on http://localhost:8000
# Frontend runs on http://localhost:3000
# Database on localhost:5432
```

### Environment Setup

Create `.env` files for each service:

**Backend (.env)**
```
DATABASE_URL=postgresql://postgres:password@db:5432/remotepay
JWT_SECRET=your-secret-key
PAYGATE_MERCHANT_ID=your-merchant-id
PAYGATE_ENCRYPTION_KEY=your-encryption-key
ALLOWED_ORIGINS=http://localhost:3000
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Project Structure

```
RemotePay/
├── backend/              # FastAPI application
│   ├── api/              # Route handlers
│   ├── services/         # Business logic
│   ├── models/           # Database models
│   ├── utils/            # Helper functions
│   ├── schemas/          # Pydantic schemas
│   ├── middleware/       # Custom middleware
│   └── main.py          # Application entry point
├── frontend/             # Next.js application
│   ├── app/              # App router
│   ├── components/       # React components
│   └── public/           # Static assets
├── database/             # PostgreSQL
│   ├── schema/           # SQL schemas
│   ├── migrations/       # Database migrations
│   └── seed/             # Seed scripts
├── docker/               # Docker configuration
│   ├── Dockerfile        # Backend image
│   └── docker-compose.yml
├── .github/workflows/    # CI/CD pipelines
├── docs/                 # Documentation
└── tests/                # Test suites
```

## API Documentation

See [docs/api-docs.md](docs/api-docs.md) for detailed API endpoints.

## Deployment

See [docs/deployment-guide.md](docs/deployment-guide.md) for deployment instructions.

## Architecture

See [docs/architecture.md](docs/architecture.md) for system design.

## Development

See [docs/developer-instructions.md](docs/developer-instructions.md) for local development setup.

## Security

This system is production-grade. All security considerations are documented in [docs/security.md](docs/security.md).

## License

MIT
