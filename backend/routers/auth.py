from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserLogin, UserResponse, Token
from backend.services.auth_service import hash_password, verify_password, create_access_token
from backend.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new Student account. Role is strictly assigned as STUDENT.
    """
    email_clean = user_in.email.strip().lower()

    # Check existing user
    existing_user = db.query(User).filter(User.email == email_clean).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email address already exists"
        )

    # Check student ID if provided
    if user_in.student_id:
        existing_sid = db.query(User).filter(User.student_id == user_in.student_id.strip()).first()
        if existing_sid:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A student with this Student ID is already registered"
            )

    new_user = User(
        name=user_in.name.strip(),
        email=email_clean,
        hashed_password=hash_password(user_in.password),
        student_id=user_in.student_id.strip() if user_in.student_id else None,
        department=user_in.department.strip() if user_in.department else None,
        role="STUDENT"  # Security: Always force STUDENT role on registration
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create JWT token
    token = create_access_token(data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role})

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with Email and Password. Returns JWT access token.
    """
    email_clean = login_data.email.strip().lower()
    user = db.query(User).filter(User.email == email_clean).first()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = create_access_token(data={"sub": str(user.id), "email": user.email, "role": user.role})

    return Token(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get profile information of the currently authenticated user.
    """
    return current_user
