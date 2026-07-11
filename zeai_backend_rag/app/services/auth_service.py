"""
Admin authentication service: verifies credentials and issues a JWT.
Wraps the low-level helpers in app.auth so main.py deals with one
call and two clear exceptions instead of manual if/else checks.
"""
from sqlalchemy.orm import Session

from app import models
from app.auth import verify_password, create_access_token


class InvalidCredentialsError(Exception):
    pass


class InactiveAccountError(Exception):
    pass


def authenticate_admin(db: Session, email: str, password: str) -> models.Admin:
    admin = db.query(models.Admin).filter(models.Admin.email == email).first()

    if not admin or not verify_password(password, admin.password_hash):
        raise InvalidCredentialsError("Invalid email or password")

    if admin.status != "active":
        raise InactiveAccountError("Admin account is inactive")

    return admin


def login(db: Session, email: str, password: str) -> dict:
    admin = authenticate_admin(db, email, password)
    token = create_access_token({"sub": str(admin.admin_id), "role": admin.role})
    return {"access_token": token, "token_type": "bearer", "admin_name": admin.name}
