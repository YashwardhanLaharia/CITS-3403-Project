# SplitMate - Project Planning

This is our single source of truth for how we build SplitMate. It covers what we're building, how we organise our work, and the conventions we follow on GitHub.

---

## What we're building

SplitMate breaks down into 7 major tasks. Each one gets a GitHub issue, a feature branch, and a PR. Smaller bugs or fixes that come up along the way get their own issues too, but these are the big ones.

### Task 1. Project setup and restructure

Get the Flask project into proper shape so everything that follows has a solid foundation.

- Create a `config.py` with separate configs for development, testing, and production. Secret keys, database URIs, and session settings all live here and read from environment variables.
- Set up the app factory pattern in `app.py` using `create_app(config)` so we can spin up different app instances for testing vs production.
- Install Flask-Migrate and initialise Alembic. All schema changes from this point forward go through migration files, not `db.create_all()`.
- Move HTML files from `frontendCode/` into `templates/` with a proper layout using Jinja2 template inheritance (`base.html` with `{% block content %}`).
- Move CSS and JS into `static/`. Update all templates to reference static files via `url_for('static', filename=...)`.
- Replace hardcoded data in templates with `{{ variables }}` passed from Flask routes. Pages should be rendered with `render_template()`, not served as static files.

### Task 2. Database models and migrations

Design and implement the data layer. Every table the app needs gets built here.

- **User** model - id, email (unique, indexed), password_hash, first_name, last_name, created_at. Extends `UserMixin` for Flask-Login.
- **Group** model - id, name, currency, invite_code (unique), created_by (FK to User), created_at.
- **Membership** model - id, user_id (FK), group_id (FK), role (e.g. "admin"/"member"), joined_at. This is the many-to-many link between users and groups.
- **Expense** model - id, group_id (FK), paid_by (FK to User), description, amount, category, date, created_at.
- Generate the initial migration with `flask db migrate` and apply it with `flask db upgrade`. Verify the schema looks right in SQLite.
- Write a `seed.py` script that populates the database with a few test users, a group, and some expenses so we can develop against realistic data.

### Task 3. Authentication

Full auth flow so users can create accounts, log in, and stay logged in.

- Register route (`POST /api/register`) - validate all fields server-side (non-empty, valid email format, password >= 8 chars, passwords match), hash with bcrypt, create user, redirect to login.
- Login route (`POST /api/login`) - look up user by email, check password hash, call `login_user()` with optional "remember me", redirect to home.
- Logout route (`POST /api/logout`) - call `logout_user()`, redirect to login with flash message.
- Protect all authenticated routes with `@login_required`. Set `login_manager.login_view` so unauthenticated users get redirected to the login page automatically.
- Profile page - display the logged-in user's info (name, email, member since). Include an edit form that lets users update their first name, last name, and password (requires entering current password to confirm).

### Task 4. Groups and invites

Let users create shared expense groups and invite others to join.

- Create group route - takes group name and currency, generates a unique invite code (e.g. 8-character alphanumeric), creates the Group row and a Membership row with role "admin" for the creator.
- Join group route - takes an invite code, validates it exists, checks the user isn't already a member, creates a Membership row with role "member".
- Home page (`/`) - query all groups the logged-in user belongs to via Membership, display them as cards with group name, member count, and total spent.
- Invite code display - once you're in a group, show the invite code somewhere obvious so you can share it with others.
- Group modal component - reusable Bootstrap modal for creating a new group. Should work on both the home page and the dashboard so we don't duplicate the form.

### Task 5. Expenses, settlements, and dashboard

The core of the app. This is where the actual expense splitting happens.

- Add expense route - takes description, amount, category, and date. Associates it with the current group and the user who paid. Saves to the Expense table.
- Dashboard page (`/group/<id>`) - pull all expenses for the group from the database. Show total spending, per-member totals, and a breakdown by category (food, transport, accommodation, etc.).
- Settlement algorithm - for each group, calculate each member's fair share (total / members), compare against what they actually paid, and generate a minimal list of transfers (e.g. "Alice pays Bob $40"). Use a greedy algorithm that matches the biggest debtor with the biggest creditor.
- Activity feed - list the most recent expenses in the group in reverse chronological order. Show who paid, the amount, category, and when.
- Wire up the "Add Expense" button on the dashboard to open a modal form. On submit, save the expense and refresh the dashboard data.

### Task 6. Security and AJAX

Harden the app and make interactions feel snappy.

- Install Flask-WTF and add CSRF tokens to every form. All POST requests should include `{{ csrf_token() }}` in a hidden field, and the server should reject requests without a valid token.
- Move the secret key out of the codebase entirely. Production reads from an env var, development uses a `.env` file loaded with python-dotenv. The `.env` file is in `.gitignore`.
- Server-side validation on all form inputs - not just auth forms but also group creation, expense submission, and profile updates. Never trust the client.
- AJAX expense submission - when the user adds an expense from the dashboard, submit via `fetch()` and update the expense list, balances, and settlement preview without a full page reload.
- AJAX balance updates - after adding an expense, recalculate and re-render the balance cards and settlement section via a JSON endpoint.

### Task 7. Testing

Prove the app works and catch regressions.

- Unit tests for models - test User password hashing (correct password returns True, wrong password returns False), test Group invite code uniqueness, test Expense creation with valid and invalid data.
- Unit tests for the settlement algorithm - test with balanced group (no transfers needed), test with one person who paid everything, test with an odd split that doesn't divide evenly.
- Unit tests for auth - test registration with duplicate email, test login with wrong password, test accessing a protected route without being logged in.
- Selenium test for signup and login - register a new user, log out, log back in, verify the home page shows the user's name.
- Selenium test for group flow - create a group, copy the invite code, log in as a different user, join the group, verify both members appear.
- Selenium test for expense flow - add an expense from the dashboard, verify it appears in the activity feed, verify balances update correctly.

---

## Branching

We use trunk-based development. `main` is the only long-lived branch - it should always be in a working state.

### Branch naming

Branches are either tied to a major task or to a standalone issue. Both follow the same format:

```
<type>/<number>-<short-description>
```

For a **major task**, the number is the task number from above:
- `feat/1-project-setup`
- `feat/3-auth`
- `feat/5-expenses-settlements`

For a **standalone issue** (a bug, a small fix, something that doesn't fit neatly into a major task), the number is the GitHub issue number:
- `fix/23-login-redirect-loop`
- `chore/29-update-dependencies`

**Types:**
- `feat/` - new functionality
- `fix/` - bug fixes
- `refactor/` - restructuring without changing behaviour
- `test/` - adding or updating tests
- `docs/` - documentation only
- `chore/` - config, dependencies, tooling

Keep descriptions short (2-4 words), lowercase, hyphens between words.

---

## Commits

We follow [Conventional Commits](https://www.conventionalcommits.org/). Every commit message looks like this:

```
<type>(<scope>): <description>

[optional body]
```

### Types

| Type | When to use |
|------|-------------|
| `feat` | Adding new functionality |
| `fix` | Fixing a bug |
| `refactor` | Changing code structure without changing behaviour |
| `style` | Formatting, whitespace - no logic changes |
| `test` | Adding or updating tests |
| `docs` | Documentation changes |
| `chore` | Dependencies, config, build tooling |

### Scopes

The scope is optional but encouraged. It says which part of the app the commit touches:

- `auth` - login, signup, sessions
- `groups` - group creation, joining, invite codes
- `expenses` - adding/viewing expenses
- `settlements` - balance calculation, who-owes-whom
- `dashboard` - the group dashboard page
- `profile` - user profile
- `db` - database models and migrations
- `ui` - general frontend/styling

### Rules

- Imperative mood: "add login route", not "added login route"
- First line under 72 characters
- The body is for *why*, not *what* - the diff shows what changed
- Reference the issue when relevant: `Closes #4`

### Examples

```
feat(auth): add password hashing with bcrypt

Passwords are now salted and hashed before storage.
Plain-text comparison replaced with bcrypt.checkpw().
Closes #3
```

```
fix(dashboard): prevent crash when group has no expenses

Template was dividing by zero when calculating averages
for a group with no expenses yet.
```

```
chore: add flask-migrate to requirements
```

```
test(auth): add unit tests for registration validation
```

---

## Issues

Every meaningful piece of work gets a GitHub issue before anyone starts coding.

### Naming

For **major tasks**, the title matches the task from the list above:
```
[<area>] <task description>
```

For **bugs**:
```
[bug] <area>: <what's broken>
```

For **smaller things** that come up during development:
```
[<area>] <what needs to happen>
```

**Examples:**
- `[setup] Project restructure and Flask app factory`
- `[auth] Implement login, signup, and session management`
- `[bug] dashboard: crash when group has no expenses`
- `[expenses] Add category dropdown to expense form`

### Descriptions

For features: a short paragraph on what needs building and a checklist of what "done" looks like.

For bugs: steps to reproduce, expected behaviour, actual behaviour.

### Labels

- `frontend` - HTML, CSS, JS, templates
- `backend` - Flask routes, logic, config
- `database` - models, migrations, schema
- `testing` - unit tests, Selenium tests
- `security` - auth, CSRF, input validation
- `bug` - something is broken

---

## Pull requests

Every branch merges into `main` via a pull request. No direct pushes.

### PR naming

Every PR title starts with the issue number in parentheses, then the issue title. If it's a major task, add `Task-N` after the issue number. The PR title should basically match the issue it closes.

```
(#<issue>) Task-<N>: <issue title>     <- major task
(#<issue>) <issue title>               <- everything else
```

**Examples:**
- `(#8) Task-3: [auth] Implement login, signup, and session management`
- `(#14) Task-5: [expenses] Expenses, settlements, and dashboard`
- `(#21) [bug] dashboard: fix crash when group has no expenses`
- `(#25) [ui] Add loading spinner to expense form`

### What goes in a PR

- Short summary of what changed and why
- Reference the issue it closes: `Closes #12`
- Checklist of things the reviewer should look at or test

### Reviews

- Every PR needs at least one approval before merging
- Leave real comments - point out things you'd change, ask questions, suggest improvements. "Looks good" on its own doesn't count.
- Address feedback before merging
- Squash merge into `main` to keep history clean

---

## Workflow

Nothing gets built without an issue, and nothing gets merged without a review.

1. **Issue first** - create a GitHub issue describing the work, label it appropriately. If it's a major task, the issue title follows the task list above.
2. **Branch** - branch off `main` following the naming convention (`feat/3-auth`, `fix/15-login-bug`, etc.)
3. **Build** - commit with conventional commit messages, reference the issue number where relevant.
4. **PR** - open a pull request against `main`. Title includes `Task-N` if it's a major task. Body references the issue with `Closes #N`.
5. **Review** - at least one teammate reviews the PR and leaves real feedback.
6. **Merge** - address any feedback, get the approval, squash merge into `main`.

Keep branches short-lived. If something takes more than a few days, break it down.
