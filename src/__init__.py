# src/__init__.py
from .api import models, schemas, database  # ← они в api/, а не в src/
from .api import auth

__all__ = ["models", "schemas", "database", "auth"]