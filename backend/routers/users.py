from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from schemas.user import UserResponse, UserUpdate
from dependencies import get_current_user
from services.auth_service import hash_password

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
def get_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get profile information for the authenticated user.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update profile details for the authenticated user.
    """
    if user_update.name is not None:
        current_user.name = user_update.name.strip()
    if user_update.student_id is not None and current_user.role == "STUDENT":
        # Check uniqueness if changing
        s_id = user_update.student_id.strip()
        existing = db.query(User).filter(User.student_id == s_id, User.id != current_user.id).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Student ID is already in use by another student"
            )
        current_user.student_id = s_id
    if user_update.department is not None:
        current_user.department = user_update.department.strip()
    if user_update.password is not None and len(user_update.password.strip()) >= 6:
        current_user.hashed_password = hash_password(user_update.password.strip())

    db.commit()
    db.refresh(current_user)
    return current_user
