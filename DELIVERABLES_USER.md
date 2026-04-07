# Deliverables for users scope

Implemented scope:
- `src/api/users.py`
- part of `src/schemas.py`
- part of `src/crud.py`
- `tests/test_users.py`

Also was added a **minimal compatibility scaffolding** so that this part can be run on its own.:
- `src/db.py`
- `src/models.py`
- `src/main.py`
- `tests/conftest.py`

## Endpoints
- `POST /users` - create user
- `GET /users/{user_id}` - get user by id
- `GET /users/search?username=<name>` - find user by username

## Local run
```bash
pytest tests/test_users.py
```
