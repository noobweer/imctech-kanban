# User CRUD Endpoints

#### GET /users
List all users.

**Auth:** Required

**Response:** `200 OK`
```json
[
  {
    "username": "test_student",
    "name": "Test Student",
    "role": "student",
    "created_at": "2026-05-03T10:00:00Z",
    "updated_at": "2026-05-03T10:00:00Z"
  },
  {
    "username": "mentor1",
    "name": "John Mentor",
    "role": "mentor",
    "created_at": "2026-05-03T09:00:00Z",
    "updated_at": "2026-05-03T09:00:00Z"
  }
]
```

---

#### GET /users/{username}
Get user by username.

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

**Errors:**
- `404` - User not found

---

#### PATCH /users/{username}
Update user.

**Auth:** Required  
**Permissions:** User can update self, or staff can update anyone

**Request:**
```json
{
  "name": "Updated Name",
  "role": "mentor",
  "password": "newpassword123"
}
```

All fields optional.

**Response:** `200 OK`
```json
{
  "username": "test_student",
  "name": "Updated Name",
  "role": "mentor",
  "created_at": "2026-05-03T10:00:00Z",
  "updated_at": "2026-05-03T11:00:00Z"
}
```

**Errors:**
- `403` - Permission denied
- `404` - User not found

---

#### DELETE /users/{username}
Delete user.

**Auth:** Required  
**Permissions:** User can delete self, or staff can delete anyone

**Response:** `200 OK`
```json
{
  "success": true
}
```

**Errors:**
- `403` - Permission denied
- `404` - User not found
