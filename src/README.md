# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

The app now uses SQLAlchemy ORM with persistent storage (MySQL-ready, with SQLite as a local default).

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install -r ../requirements.txt
   ```

2. Optional: configure MySQL with an environment variable:

   ```
   export DATABASE_URL="mysql+pymysql://user:password@localhost:3306/mergington"
   ```

   If `DATABASE_URL` is not set, the app uses a local SQLite database at `school.db`.

3. Run the application:

   ```
   uvicorn app:app --reload
   ```

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Users** - Uses email as identifier:
   - Name
   - Role

3. **Memberships** - Tracks which users are enrolled in which activities.

4. **Club Requests** - Tracks pending and resolved membership requests.

Data is persisted in the configured database, so it remains available across server restarts.
