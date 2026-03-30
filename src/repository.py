"""Repository layer for activity operations."""

from sqlalchemy.orm import Session, selectinload

from models import Activity, Membership, User

INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"],
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"],
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"],
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"],
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"],
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"],
    },
}


class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def seed_if_empty(self) -> None:
        if self.db.query(Activity).count() > 0:
            return

        for activity_name, details in INITIAL_ACTIVITIES.items():
            activity = Activity(
                name=activity_name,
                description=details["description"],
                schedule=details["schedule"],
                max_participants=details["max_participants"],
            )
            self.db.add(activity)
            self.db.flush()

            for email in details["participants"]:
                user = self._get_or_create_user(email)
                self.db.add(Membership(user_id=user.id, activity_id=activity.id))

        self.db.commit()

    def get_activities(self) -> dict:
        rows = (
            self.db.query(Activity)
            .options(selectinload(Activity.memberships).selectinload(Membership.user))
            .order_by(Activity.name.asc())
            .all()
        )

        return {
            activity.name: {
                "description": activity.description,
                "schedule": activity.schedule,
                "max_participants": activity.max_participants,
                "participants": [m.user.email for m in activity.memberships if m.user],
            }
            for activity in rows
        }

    def signup_for_activity(self, activity_name: str, email: str) -> None:
        activity = self.db.query(Activity).filter(Activity.name == activity_name).first()
        if not activity:
            raise ValueError("Activity not found")

        current_participants = self.db.query(Membership).filter(Membership.activity_id == activity.id).count()
        if current_participants >= activity.max_participants:
            raise ValueError("Activity is full")

        user = self._get_or_create_user(email)

        already_joined = (
            self.db.query(Membership)
            .filter(Membership.activity_id == activity.id, Membership.user_id == user.id)
            .first()
        )
        if already_joined:
            raise ValueError("Student is already signed up")

        self.db.add(Membership(user_id=user.id, activity_id=activity.id))
        self.db.commit()

    def unregister_from_activity(self, activity_name: str, email: str) -> None:
        activity = self.db.query(Activity).filter(Activity.name == activity_name).first()
        if not activity:
            raise ValueError("Activity not found")

        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise ValueError("Student is not signed up for this activity")

        membership = (
            self.db.query(Membership)
            .filter(Membership.activity_id == activity.id, Membership.user_id == user.id)
            .first()
        )
        if not membership:
            raise ValueError("Student is not signed up for this activity")

        self.db.delete(membership)
        self.db.commit()

    def _get_or_create_user(self, email: str) -> User:
        user = self.db.query(User).filter(User.email == email).first()
        if user:
            return user

        user = User(email=email)
        self.db.add(user)
        self.db.flush()
        return user
