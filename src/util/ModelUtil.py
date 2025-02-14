from enum import Enum

from src.extensions import db


def create_attribute_enum(model_class: db.Model, enum_name: str) -> Enum:
    """Dynamically creates an Enum from a SQLAlchemy models columns."""
    members = {}
    for column in model_class.__table__.columns:
        member_name = column.name.upper()
        members[member_name] = column.name

    return Enum(enum_name, members)
