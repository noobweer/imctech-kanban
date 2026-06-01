# Project CRUD Endpoints

#### GET /projects
List all projects accessible to the user.
*   **Auth:** Required
*   **Access:** User sees projects where they own or are a member of at least one board. Staff sees all.

#### POST /projects
Create a new project.
*   **Auth:** Required
*   **Access:** Mentor or staff (Students restricted).

#### GET /projects/{project_id}
Get project details.
*   **Auth:** Required

#### PATCH /projects/{project_id}
Update project name.
*   **Auth:** Required

#### DELETE /projects/{project_id}
Delete project (fails if boards exist).
*   **Auth:** Required
