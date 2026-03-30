"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

from database import SessionLocal, get_db, init_db
from repository import ActivityRepository
from sqlalchemy.orm import Session

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.on_event("startup")
def startup() -> None:
    init_db()

    # Seed once so existing demo behavior still works after enabling persistence.
    db = SessionLocal()
    try:
        ActivityRepository(db).seed_if_empty()
    finally:
        db.close()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    return ActivityRepository(db).get_activities()


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    repository = ActivityRepository(db)
    try:
        repository.signup_for_activity(activity_name=activity_name, email=email)
    except ValueError as error:
        detail = str(error)
        status_code = 404 if detail == "Activity not found" else 400
        raise HTTPException(status_code=status_code, detail=detail) from error

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    repository = ActivityRepository(db)
    try:
        repository.unregister_from_activity(activity_name=activity_name, email=email)
    except ValueError as error:
        detail = str(error)
        status_code = 404 if detail == "Activity not found" else 400
        raise HTTPException(status_code=status_code, detail=detail) from error

    return {"message": f"Unregistered {email} from {activity_name}"}
