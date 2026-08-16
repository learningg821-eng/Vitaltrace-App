from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from auth.jwt import decode_token
from auth.models import User
from database import get_db


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:

    print("\n========== AUTH DEBUG ==========")
    print("TOKEN RECEIVED:", bool(token))

    if not token:
        print("❌ NO TOKEN")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token",
        )

    try:
        payload = decode_token(token)

        print("JWT PAYLOAD:", payload)

        user_id = payload.get("sub")

        print("TOKEN SUB:", user_id)

        if user_id is None:
            print("❌ SUB IS MISSING")

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not contain user ID",
            )

        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            print("❌ INVALID USER ID:", user_id)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
            )

        user = (
            db.query(User)
            .filter(User.id == user_id)
            .first()
        )

        print("DATABASE USER:", user)

        if user is None:
            print("❌ USER NOT FOUND:", user_id)

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        print("✅ AUTH SUCCESS:", user.username)
        print("================================\n")

        return user

    except HTTPException:
        raise

    except Exception as e:
        print("❌ AUTH EXCEPTION:", repr(e))

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
        )


def require_permission(action: str):

    def checker(
        current_user: User = Depends(get_current_user)
    ):
        user_permissions = [
            permission.action
            for permission in current_user.role.permissions
        ]

        if action not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

    return Depends(checker)