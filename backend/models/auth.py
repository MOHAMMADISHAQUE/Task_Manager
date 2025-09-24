from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
import uuid

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    picture: Optional[str] = None
    auth_provider: str = "email"  # "email" or "emergent"
    password_hash: Optional[str] = None  # Only for email auth
    google_id: Optional[str] = None  # Only for emergent auth
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PasswordResetToken(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    token: str
    expires_at: datetime
    used: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Request/Response Models
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str

class EmergentSessionRequest(BaseModel):
    session_id: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    picture: Optional[str] = None
    auth_provider: str

class AuthResponse(BaseModel):
    user: UserResponse
    message: str