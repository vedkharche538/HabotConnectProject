from flask_sqlalchemy import SQLAlchemy
from app import app_instance
from datetime import datetime
from typing import Optional

db = SQLAlchemy(app_instance)


class Employee(db.Model):
    __tablename__ = 'employees'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name: str = db.Column(db.String(100), nullable=False, unique=True)
    email: str = db.Column(db.String(100), nullable=False, unique=True)
    department: Optional[str] = db.Column(db.String(100), nullable=True)
    role: Optional[str] = db.Column(db.String(100), nullable=True)
    date_joined: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Employee(name={self.name}, email={self.email})>"

    def to_dict(self) -> dict:
        """Convert the Employee instance to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "role": self.role,
            "date_joined": self.date_joined.isoformat()  # Format date as ISO string
        }