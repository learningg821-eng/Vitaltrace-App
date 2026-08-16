from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
    )


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String, unique=True, nullable=False)

    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions",
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    role_id = Column(
        Integer,
        ForeignKey("roles.id"),
        nullable=False,
    )

    role = relationship("Role")

    fcm_tokens = relationship(
        "FCMDeviceToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class FCMDeviceToken(Base):
    __tablename__ = "fcm_device_tokens"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    token = Column(
        String,
        unique=True,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="fcm_tokens",
    )