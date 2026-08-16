from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.models import Role, Permission
from auth.schemas import RoleCreate, RoleSchema, AssignPermission
from auth.dependencies import require_permission
from database import get_db

router = APIRouter(prefix="/roles", tags=["Roles"])


def get_role_or_404(role_id: int, db: Session) -> Role:
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return role


@router.get("/", response_model=list[RoleSchema], dependencies=[require_permission("role:read")])
def list_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()


@router.post("/", response_model=RoleSchema, status_code=status.HTTP_201_CREATED, dependencies=[require_permission("role:create")])
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    if db.query(Role).filter(Role.name == payload.name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")

    role = Role(name=payload.name)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[require_permission("role:delete")])
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = get_role_or_404(role_id, db)
    db.delete(role)
    db.commit()


@router.get("/{role_id}/permissions", response_model=RoleSchema, dependencies=[require_permission("role:read")])
def get_role_permissions(role_id: int, db: Session = Depends(get_db)):
    return get_role_or_404(role_id, db)


@router.post("/{role_id}/permissions", response_model=RoleSchema, dependencies=[require_permission("role:assign")])
def assign_permission(role_id: int, payload: AssignPermission, db: Session = Depends(get_db)):
    role       = get_role_or_404(role_id, db)
    permission = db.query(Permission).filter(Permission.id == payload.permission_id).first()

    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found")

    if permission in role.permissions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already assigned")

    role.permissions.append(permission)
    db.commit()
    db.refresh(role)
    return role


@router.delete("/{role_id}/permissions/{permission_id}", response_model=RoleSchema, dependencies=[require_permission("role:assign")])
def revoke_permission(role_id: int, permission_id: int, db: Session = Depends(get_db)):
    role       = get_role_or_404(role_id, db)
    permission = db.query(Permission).filter(Permission.id == permission_id).first()

    if not permission or permission not in role.permissions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission not assigned to role")

    role.permissions.remove(permission)
    db.commit()
    db.refresh(role)
    return role