# RemotePay API Documentation

## Base URL
- Local: `http://localhost:8000`
- Production: `https://api.remote-pay.co.za`

## Endpoints

### Health Check
`GET /health`

### Customers
`POST /api/v1/customers`
`GET /api/v1/customers/{customer_id}`

### Payments
`POST /api/v1/payments`
`GET /api/v1/payments/{transaction_id}`

### Assistant
`POST /api/v1/assistant/config`
`GET /api/v1/assistant/{assistant_id}`

### Plans
`GET /api/v1/plans`

### Webhooks
`POST /webhooks/payfast`

## Test Card
- Number: `4111111111111111`
- Expiry: Any future date
- CVV: Any 3 digits
