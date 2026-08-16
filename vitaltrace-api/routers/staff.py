from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

import models
import schemas
from auth.models import User, Role
from auth.dependencies import require_permission
from database import get_db

router   = APIRouter(prefix="/api/staff", tags=["Staff"])
pwd_ctx  = CryptContext(schemes=["bcrypt"])


def get_staff_or_404(staff_id: int, db: Session) -> models.Staff:
    staff = db.query(models.Staff).filter(models.Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Staff not found")
    return staff


def format_staff(staff: models.Staff, db: Session) -> dict:
    user = db.query(User).filter(User.id == staff.user_id).first()
    return {
        "id":         staff.id,
        "user_id": staff.user_id,
        "staffId":    staff.staff_id,    # ← camelCase
        "firstName":  staff.first_name,  # ← camelCase
        "lastName":   staff.last_name,   # ← camelCase
        "department": staff.department,
        "shift":      staff.shift,
        "phone":      staff.phone,
        "status":     staff.status,
        "username":   user.username if user else None,
        "role":       user.role.name if user else None,
        "role_id":    user.role_id if user else None,
    }


@router.get("/", dependencies=[require_permission("staff:read")])
def list_staff(db: Session = Depends(get_db)):
    staff_list = db.query(models.Staff).all()
    return [format_staff(s, db) for s in staff_list]


@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[require_permission("staff:create")])
def create_staff(payload: schemas.StaffCreate, db: Session = Depends(get_db)):
    # check username unique
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    # check role exists
    role = db.query(Role).filter(Role.id == payload.role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

    # create user first
    user = User(
        username=payload.username,
        password=pwd_ctx.hash(payload.password),
        role_id=payload.role_id,
    )
    db.add(user)
    db.flush()  # ← get user.id

    # create staff with user_id
    staff = models.Staff(
        first_name=payload.firstName,
        last_name=payload.lastName,
        department=payload.department,
        shift=payload.shift,
        phone=payload.phone,
        status=payload.status,
        user_id=user.id,  # ← set immediately
    )
    db.add(staff)
    db.flush()  # ← get staff.id

    staff.staff_id = f"ST-{staff.id:04d}"  # ← now set staff_id

    db.commit()
    db.refresh(staff)

    return format_staff(staff, db)

@router.put("/{staff_id}", dependencies=[require_permission("staff:update")])
def update_staff(staff_id: int, payload: schemas.StaffCreate, db: Session = Depends(get_db)):
    staff = get_staff_or_404(staff_id, db)
    user  = db.query(User).filter(User.id == staff.user_id).first()

    staff.first_name = payload.firstName
    staff.last_name  = payload.lastName
    staff.department = payload.department
    staff.shift      = payload.shift
    staff.phone      = payload.phone
    staff.status     = payload.status

    if user:
        user.role_id = payload.role_id
        if payload.password:
            user.password = pwd_ctx.hash(payload.password)

    db.commit()
    db.refresh(staff)

    return format_staff(staff, db)


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[require_permission("staff:delete")])
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    staff = get_staff_or_404(staff_id, db)

    # delete linked user too
    user = db.query(User).filter(User.id == staff.user_id).first()
    if user:
        db.delete(user)

    db.delete(staff)
    db.commit()