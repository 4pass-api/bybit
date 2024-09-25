# FastAPI Backend Template

This is a template for a FastAPI backend project. It includes a basic structure for the project, a Dockerfile, and a docker-compose file.

## Features

- FastAPI
- OAuth2 with Password (and hashing), Bearer with JWT tokens
- Docker
- Docker Compose
- MySQL

## API Documentation

1. Swagger UI: `/docs`
2. ReDoc: `/redoc`
3. Stoplight Elements: `/elements`

## Init Database

```bash
docker compose up init -d
```

### Test data

```
username: test-username
password: test-password
```