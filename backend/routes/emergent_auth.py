from fastapi import APIRouter, HTTPException, status, Response, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
import httpx
import logging
from models.auth import (
    UserResponse, AuthResponse, User, Session, EmergentSessionRequest
)
from auth.utils import (
    generate_session_token, hash_token, get_session_expiry
)
from seed_data import initialize_new_user

logger = logging.getLogger(__name__)

def create_emergent_auth_router(db: AsyncIOMotorDatabase) -> APIRouter:
    """Create Emergent auth router with database dependency injected."""
    
    router = APIRouter(prefix="/auth/emergent", tags=["emergent-authentication"])
    
    @router.get("/login")
    async def emergent_login(redirect_url: str = None):
        """Initiate Emergent Auth login flow."""
        
        if not redirect_url:
            # Default redirect to dashboard after login
            redirect_url = "http://localhost:3000/dashboard"
        
        # Redirect to Emergent Auth
        auth_url = f"https://auth.emergentagent.com/?redirect={redirect_url}"
        
        return {"auth_url": auth_url}
    
    @router.post("/callback", response_model=AuthResponse)
    async def emergent_callback(
        session_request: EmergentSessionRequest, 
        response: Response
    ):
        """Handle Emergent Auth callback and process session."""
        
        try:
            # Get user data from Emergent Auth service
            async with httpx.AsyncClient() as client:
                emergent_response = await client.get(
                    "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                    headers={"X-Session-ID": session_request.session_id}
                )
                
                if emergent_response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid session ID"
                    )
                
                user_data = emergent_response.json()
                
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to validate session with Emergent Auth"
            )
        
        # Check if user exists by email or google_id
        existing_user = await db.users.find_one({
            "$or": [
                {"email": user_data["email"]},
                {"google_id": user_data["id"]}
            ]
        })
        
        user_id = None
        is_new_user = False
        
        if existing_user:
            user_id = existing_user["id"]
            
            # If user exists with email auth, upgrade to support both
            if existing_user.get("auth_provider") == "email":
                await db.users.update_one(
                    {"id": user_id},
                    {
                        "$set": {
                            "google_id": user_data["id"],
                            "picture": user_data.get("picture"),
                            "updated_at": datetime.now(timezone.utc)
                        }
                    }
                )
                logger.info(f"Linked Emergent Auth to existing email user: {user_id}")
            
        else:
            # Create new user with Emergent Auth
            user = User(
                name=user_data["name"],
                email=user_data["email"],
                picture=user_data.get("picture"),
                auth_provider="emergent",
                google_id=user_data["id"]
            )
            
            await db.users.insert_one(user.dict())
            user_id = user.id
            is_new_user = True
            
            # Initialize new user with sample data
            try:
                await initialize_new_user(user_id)
                logger.info(f"Sample data created for new Emergent user: {user_id}")
            except Exception as e:
                logger.error(f"Failed to create sample data for user {user_id}: {e}")
        
        # Get updated user data
        user_doc = await db.users.find_one({"id": user_id})
        
        # Create session with the emergent session token for validation
        session_token = user_data["session_token"]
        hashed_session_token = hash_token(session_token)
        
        session = Session(
            user_id=user_id,
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
            id=user_doc["id"],
            name=user_doc["name"],
            email=user_doc["email"],
            picture=user_doc.get("picture"),
            auth_provider=user_doc.get("auth_provider", "emergent")
        )
        
        message = "Account created successfully" if is_new_user else "Login successful"
        
        return AuthResponse(
            user=user_response,
            message=message
        )
    
    return router