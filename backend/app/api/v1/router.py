from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import select

from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token
from app.db.session import get_session
from app.models import User


api_v1_router = APIRouter(prefix="/auth", tags=["authentication"])


class RegisterRequest(BaseModel):
    email: str
    password: str
    organization_name: str


class LoginRequest(BaseModel):
    email: str
    password: str


@api_v1_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    session=Depends(get_session),
):
    """Register a new user."""
    email = payload.email
    password = payload.password
    organization_name = payload.organization_name

    # Check if user already exists
    statement = select(User).where(User.email == email)
    result = session.execute(statement)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create organization
    from app.models import Organization
    org = Organization(name=organization_name, plan_type="free")
    session.add(org)
    session.commit()
    session.refresh(org)
    
    # Create user
    hashed_password = hash_password(password)
    user = User(
        email=email,
        password_hash=hashed_password,
        organization_id=org.id,
        organization_ids=[org.id],
        role="owner",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Create access token
    access_token = create_access_token(subject=user.email)
    
    return {"access_token": access_token, "token_type": "bearer"}


@api_v1_router.post("/login")
def login(
    payload: LoginRequest,
    session=Depends(get_session),
):
    """Login and get access token."""
    email = payload.email
    password = payload.password

    # Find user
    statement = select(User).where(User.email == email)
    result = session.execute(statement)
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(subject=user.email)
    
    return {"access_token": access_token, "token_type": "bearer"}