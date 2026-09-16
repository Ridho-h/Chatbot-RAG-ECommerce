"""
User model, role enum, and in-memory user store.
Uses bcrypt directly for password hashing (passlib is incompatible with bcrypt>=4.1).
"""

import uuid
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

import bcrypt


class Role(str, Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    CUSTOMER = "customer"


def _hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


@dataclass
class User:
    """User model with hashed password and role."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    username: str = ""
    hashed_password: str = ""
    role: Role = Role.CUSTOMER

    def verify_password(self, password: str) -> bool:
        """Verify a plain-text password against the stored hash."""
        return _verify_password(password, self.hashed_password)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain-text password."""
        return _hash_password(password)


class UserStore:
    """
    Simple in-memory user store.
    For production, replace with a database (SQLite, PostgreSQL, etc.).
    """

    def __init__(self):
        self._users: dict[str, User] = {}  # username -> User

    def create_user(
        self,
        username: str,
        password: str,
        role: Role = Role.CUSTOMER,
    ) -> User:
        """
        Create a new user.

        Raises:
            ValueError: If username already exists.
        """
        if username in self._users:
            raise ValueError(f"User '{username}' already exists")

        user = User(
            username=username,
            hashed_password=User.hash_password(password),
            role=role,
        )
        self._users[username] = user
        return user

    def get_user(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self._users.get(username)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user with username and password.

        Returns:
            User if credentials are valid, None otherwise.
        """
        user = self.get_user(username)
        if user and user.verify_password(password):
            return user
        return None

    def get_user_count(self) -> int:
        """Return total number of registered users."""
        return len(self._users)

    def seed_admin(self, username: str, password: str) -> User:
        """
        Seed an admin user if it doesn't exist.
        Called during application startup.
        """
        existing = self.get_user(username)
        if existing:
            return existing
        return self.create_user(username, password, Role.ADMIN)


# Singleton instance
user_store = UserStore()
