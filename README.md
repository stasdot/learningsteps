# LearningSteps API

LearningSteps is a FastAPI + PostgreSQL backend for tracking a personal learning journal.
It is built and deployed as a real backend service with authentication, persistence, and cloud deployment.

This project focuses on **practical backend engineering**, not local-only demos.

---

## Overview

The API allows authenticated users to create, update, and delete journal entries, while allowing public read access to entries.

It is deployed on cloud virtual machines and runs behind nginx using systemd.

---

## Features

* FastAPI async REST API
* PostgreSQL database (asyncpg)
* JWT authentication
* Rate limiting
* Simple in-memory caching
* Structured logging
* nginx reverse proxy
* systemd-managed service
* Cloud VM deployment

---

## API Endpoints

### Authentication

| Method | Endpoint      | Description               |
| -----: | ------------- | ------------------------- |
|   POST | `/auth/login` | Obtain a JWT access token |

Login uses query parameters (`username`, `password`) and returns a JWT token.

---

### Journal Entries (v1)

| Method | Endpoint           | Auth Required | Description        |
| -----: | ------------------ | ------------- | ------------------ |
|   POST | `/v1/entries`      | Yes           | Create a new entry |
|    GET | `/v1/entries`      | No            | Get all entries    |
|    GET | `/v1/entries/{id}` | No            | Get a single entry |
|  PATCH | `/v1/entries/{id}` | Yes           | Update an entry    |
| DELETE | `/v1/entries/{id}` | Yes           | Delete an entry    |
| DELETE | `/v1/entries`      | Yes           | Delete all entries |

---

## Authentication Flow

1. Call `/auth/login`
2. Receive an access token
3. Send requests with the header:

```
Authorization: Bearer <token>
```

Protected endpoints require a valid token.

Swagger UI supports authentication via the **Authorize** button.

---

## Project Structure

```
api/
├── main.py
├── routers/
│   ├── auth_router.py
│   └── journal_router.py
├── services/
│   └── entry_service.py
├── repositories/
│   └── postgres_repository.py
├── models/
│   └── entry.py
├── dependencies/
│   ├── auth.py
│   ├── rate_limit.py
│   └── cache.py
```

### Architecture rules

* Routers handle HTTP and validation
* Services coordinate business logic
* Repositories handle database access
* Timestamps and IDs are generated only in repositories
* Models are used only for input and output validation

---

## Database Schema

```sql
entries (
  id          UUID PRIMARY KEY,
  data        JSONB NOT NULL,
  created_at  TIMESTAMP NOT NULL,
  updated_at  TIMESTAMP NOT NULL
)
```

All timestamps are stored as UTC (naive) and generated in the repository layer.

---

## Running the API

### Requirements

* Python 3.10+
* PostgreSQL
* nginx
* systemd (Linux)

### Environment variables

Create a `.env` file (not committed):

```env
DATABASE_URL=postgresql://user:password@db-host:5432/learningsteps
JWT_SECRET_KEY=change-me
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

---

### Service management

The API runs as a systemd service:

```bash
sudo systemctl start learningsteps-api
sudo systemctl status learningsteps-api
```

nginx proxies external traffic to the application.

---

## Testing

### Health check

```bash
curl http://localhost/health
```

### Login

```bash
curl -X POST "http://localhost/auth/login?username=admin&password=admin"
```

### Create entry

```bash
curl -X POST http://localhost/v1/entries \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "work": "worked on backend auth",
    "struggle": "debugging datetime issues",
    "intention": "keep layers clean"
  }'
```

---

## Troubleshooting

### API does not start

* Check logs:

  ```bash
  journalctl -u learningsteps-api -n 50
  ```
* Verify environment variables are set in systemd
* Confirm PostgreSQL is reachable

### Unauthorized responses

* Token is missing, expired, or invalid
* Re-authenticate via `/auth/login`

### Validation errors

* Request body does not match the expected schema
* Check FastAPI error details in the response

---

## Notes

This project intentionally surfaces real backend issues such as:

* JWT authentication wiring
* systemd and virtual environment interaction
* nginx reverse proxy debugging
* datetime ownership across layers
* asyncpg and PostgreSQL behavior
* strict separation of concerns

---

## License

MIT License.
