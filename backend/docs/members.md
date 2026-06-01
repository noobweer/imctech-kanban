# Members Endpoints

#### GET /boards/{board_id}/members
List all members including owner.
*   **Auth:** Required
*   **Access:** Owner, member, or staff.
*   **Notes:** Owner is always first with `is_owner: true`. No password returned.

#### DELETE /boards/{board_id}/members/{username}
Remove a member from a board.
*   **Auth:** Required
*   **Access:** Board owner or staff.
*   **Condition:** Cannot remove the board owner.

#### POST /boards/{board_id}/leave
Leave a board as the current user.
*   **Auth:** Required
*   **Access:** Any member.
*   **Condition:** Owner cannot leave.
