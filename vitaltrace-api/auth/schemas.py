from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"


class PermissionSchema(BaseModel):
    id:     int
    action: str

    class Config:
        from_attributes = True


class RoleSchema(BaseModel):
    id:          int
    name:        str
    permissions: list[PermissionSchema] = []

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str


class PermissionCreate(BaseModel):
    action: str


class AssignPermission(BaseModel):
    permission_id: int