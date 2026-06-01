# Auth Endpoints

#### POST /auth/register
Register new user.

**Request:**
```json
{
  "username": "test_student",
  "password": "12345678",
  "name": "Test Student",
  "role": "student"
}
```

**Response:** `200 OK`
```json
{
  "username": "test_student",
  "name": "Test Student",
  "role": "student",
  "created_at": "2026-05-03T10:00:00Z",
  "updated_at": "2026-05-03T10:00:00Z"
}
```

**Errors:**
- `400` - Username already exists

---

#### POST /token/pair
Login and get JWT tokens.

**Request:**
```json
{
  "username": "test_student",
  "password": "12345678"
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Errors:**
- `401` - Invalid credentials

---

#### POST /token/refresh
Refresh access token.

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK`
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

#### GET /auth/me
Get current authenticated user.

**Auth:** Required

**Response:** `200 OK`
```json
{
  "username": "test_student",
  "name": "Test Student",
  "role": "student",
  "created_at": "2026-05-03T10:00:00Z",
  "updated_at": "2026-05-03T10:00:00Z"
}
```
