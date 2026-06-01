# Invite Endpoints

#### GET /boards/{board_id}/invites
List all invites for a board.
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### GET /boards/{board_id}/invites/current
Get current active invite for a board.
*   **Auth:** Required
*   **Access:** Board owner or staff.
*   **Condition:** Returns `404` if no active invite exists.

#### POST /boards/{board_id}/invites
Create a new invite. Deactivates all existing active invites for this board.
*   **Auth:** Required
*   **Access:** Board owner or staff.
*   **Body:** `expires_in_days` (int, default 7), `max_uses` (int or null for Unlimited).

#### GET /invites/{invite_id}
Get invite details.
*   **Auth:** Required
*   **Access:** Owner/staff get full info. Any authenticated user gets public info (is_active, is_expired, board_name).

#### PATCH /invites/{invite_id}
Update invite settings (expires_in_days, expire_at, max_uses, is_active).
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### DELETE /invites/{invite_id}
Soft-deactivate invite (sets `is_active = false`, does not delete).
*   **Auth:** Required
*   **Access:** Board owner or staff.

#### POST /invites/{invite_id}/join
Join a board via invite link. Adds user to `Board.members`, increments `used_count`.
*   **Auth:** Required
*   **Access:** Any authenticated user.
*   **Condition:** Invite must be active, not expired, not exhausted. Already owner/member returns `200` with no side effects.
