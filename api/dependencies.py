"""FastAPI dependencies injection."""

from fastapi import Depends
from sqlalchemy.orm import Session
from src.database.session import get_db

# Re-export get_db for clean route injection
__all__ = ["get_db", "Depends", "Session"]
