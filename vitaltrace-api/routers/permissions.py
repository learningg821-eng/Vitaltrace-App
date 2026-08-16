from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.models import Permission
from auth.schemas import PermissionCreate, PermissionSchema
from auth.dependencies import require_permission
from database import get_db

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.get("/", response_model=list[PermissionSchema], dependencies=[require_permission("permission:read")])
def list_permissions(db: Session = Depends(get_db)):
    return db.query(Permission).all()


@router.post("/", response_model=PermissionSchema, status_code=status.HTTP_201_CREATED, dependencies=[require_permission("permission:create")])
def create_permission(payload: PermissionCreate, db: Session = Depends(get_db)):
    if db.query(Permission).filter(Permission.action == payload.action).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Permission already exists")

    permission = Permission(action=payload.action)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


@router.delete("/{permission_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[require_permission("permission:delete")])
def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    permission = db.query(Permission).filter(Permission.id == permission_id).first()

    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    db.delete(permission)
    db.commit()