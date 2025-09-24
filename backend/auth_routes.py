from fastapi import APIRouter, HTTPException, status, Response, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from models.auth import (
    SignupRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest,
    UserResponse, AuthResponse, User, Session, PasswordResetToken
)
from auth.utils import (
    verify_password, get_password_hash, generate_session_token, 
    generate_reset_token, hash_token, get_session_expiry, get_reset_token_expiry
)
from auth.dependencies import get_current_user
from seed_data import initialize_new_user
import logging

logger = logging.getLogger(__name__)

def create_auth_router(db: AsyncIOMotorDatabase) -> APIRouter:
    """Create auth router with database dependency injected."""
    
    router = APIRouter(prefix="/auth", tags=["authentication"])
    
    @router.post("/signup", response_model=AuthResponse)
    async def signup(user_data: SignupRequest, response: Response):
        """Register a new user with email and password."""
        
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Validate password strength
        if len(user_data.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Create new user
        password_hash = get_password_hash(user_data.password)
        
        user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=password_hash,
            auth_provider="email"
        )
        
        # Save user to database
        await db.users.insert_one(user.dict())
        
        # Create session
        session_token = generate_session_token()
        hashed_session_token = hash_token(session_token)
        
        session = Session(
            user_id=user.id,
            session_token=hashed_session_token,
            expires_at=get_session_expiry()
        )
        
        await db.sessions.insert_one(session.dict())
        
        # Set secure cookie
        response.set_cookie(
            "session_token",
            session_token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            secure=True,
            samesite="none",
            path="/"
        )
        
        user_response = UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            picture=user.picture,
            auth_provider=user.auth_provider
        )
        
        return AuthResponse(
            user=user_response,
            message="Account created successfully"
        )

    @router.post("/login", response_model=AuthResponse)
    async def login(credentials: LoginRequest, response: Response):
        """Authenticate user with email and password."""
        
        # Find user by email
        user = await db.users.find_one({"email": credentials.email})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Verify password
        if not user.get("password_hash") or not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create session
        session_token = generate_session_token()
        hashed_session_token = hash_token(session_token)
        
        session = Session(
            user_id=user["id"],
            session_token=hashed_session_token,
            expires_at=get_session_expiry()
        )
        
        await db.sessions.insert_one(session.dict())
        
        # Set secure cookie
        response.set_cookie(
            "session_token",
            session_token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            secure=True,
            samesite="none",
            path="/"
        )
        
        user_response = UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            picture=user.get("picture"),
            auth_provider=user.get("auth_provider", "email")
        )
        
        return AuthResponse(
            user=user_response,
            message="Login successful"
        )

    @router.get("/me", response_model=UserResponse)
    async def get_current_user_info(request: Request):
        """Get current authenticated user information."""
        
        user = await get_current_user(request, db)
        
        return UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            picture=user.get("picture"),
            auth_provider=user.get("auth_provider", "email")
        )

    @router.post("/logout")
    async def logout(request: Request, response: Response):
        """Logout user and invalidate session."""
        
        try:
            # Get session token
            session_token = request.cookies.get("session_token")
            
            if session_token:
                hashed_token = hash_token(session_token)
                # Delete session from database
                await db.sessions.delete_one({"session_token": hashed_token})
            
            # Clear cookie
            response.delete_cookie("session_token", path="/")
            
            return {"message": "Logout successful"}
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            # Still clear the cookie even if database operation fails
            response.delete_cookie("session_token", path="/")
            return {"message": "Logout completed"}

    @router.post("/forgot-password")
    async def forgot_password(request: ForgotPasswordRequest):
        """Send password reset email."""
        
        # Find user by email
        user = await db.users.find_one({"email": request.email})
        
        if not user:
            # Don't reveal if email exists, always return success
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Only allow password reset for email auth users
        if user.get("auth_provider") != "email":
            return {"message": "Password reset is only available for email accounts"}
        
        # Generate reset token
        reset_token = generate_reset_token()
        
        # Save reset token to database
        password_reset = PasswordResetToken(
            user_id=user["id"],
            token=reset_token,
            expires_at=get_reset_token_expiry()
        )
        
        await db.password_reset_tokens.insert_one(password_reset.dict())
        
        # TODO: Send email with reset link
        # For now, just log the token (in production, send via email)
        reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
        logger.info(f"Password reset link for {request.email}: {reset_link}")
        
        return {"message": "If the email exists, a reset link has been sent"}

    @router.post("/reset-password")
    async def reset_password(request: ResetPasswordRequest):
        """Reset user password using reset token."""
        
        # Find valid reset token
        reset_token = await db.password_reset_tokens.find_one({
            "token": request.token,
            "used": False,
            "expires_at": {"$gt": datetime.now(timezone.utc)}
        })
        
        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Validate new password
        if len(request.password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        
        # Update user password
        password_hash = get_password_hash(request.password)
        
        await db.users.update_one(
            {"id": reset_token["user_id"]},
            {
                "$set": {
                    "password_hash": password_hash,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Mark token as used
        await db.password_reset_tokens.update_one(
            {"_id": reset_token["_id"]},
            {"$set": {"used": True}}
        )
        
        # Invalidate all existing sessions for this user
        await db.sessions.delete_many({"user_id": reset_token["user_id"]})
        
        return {"message": "Password reset successful"}
    
    return router