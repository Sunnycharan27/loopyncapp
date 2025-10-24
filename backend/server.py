from fastapi import FastAPI, APIRouter, HTTPException, Body, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import socketio
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import shutil
import razorpay
import jwt

# Import the Google Sheets database module
from sheets_db import init_sheets_db

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize Google Sheets Database (in demo mode for now)
sheets_db = init_sheets_db(demo_mode=True)

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-this-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Security scheme for auth
security = HTTPBearer()

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',  # In production, restrict this
    logger=True,
    engineio_logger=True
)

# Mount Socket.IO to the FastAPI app
sio_asgi_app = socketio.ASGIApp(sio)
app.mount('/socket.io', sio_asgi_app)

# Store connected clients: {userId: sid}
connected_clients = {}

# Create uploads directory
UPLOAD_DIR = Path("/app/backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Serve uploaded files as static (mounted under both /uploads and /api/uploads for ingress)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/api/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads_api")

# ===== AI (Emergent Integrations) =====
try:
    from emergentintegrations.llm.chat import LlmChat, UserMessage, FileContentWithMimeType
    EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
    if not EMERGENT_LLM_KEY:
        logging.warning("EMERGENT_LLM_KEY not set; AI endpoints will return 503")
except Exception as e:
    logging.error(f"Failed to import emergentintegrations: {e}")
    LlmChat = None
    UserMessage = None
    FileContentWithMimeType = None



# ===== MODELS =====

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    handle: str
    name: str
    avatar: str = "https://api.dicebear.com/7.x/avataaars/svg?seed=default"
    bio: str = ""
    kycTier: int = 1
    walletBalance: float = 0.0
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserCreate(BaseModel):
    handle: str
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    created_at: str

class Post(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    authorId: str
    text: str
    media: Optional[str] = None
    audience: str = "public"
    stats: dict = Field(default_factory=lambda: {"likes": 0, "quotes": 0, "reposts": 0, "replies": 0})
    likedBy: List[str] = Field(default_factory=list)
    repostedBy: List[str] = Field(default_factory=list)
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PostCreate(BaseModel):
    text: str
    media: Optional[str] = None
    audience: str = "public"

class Reel(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    authorId: str
    videoUrl: str
    thumb: str
    caption: str = ""
    stats: dict = Field(default_factory=lambda: {"views": 0, "likes": 0, "comments": 0})
    likedBy: List[str] = Field(default_factory=list)
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ReelCreate(BaseModel):
    videoUrl: str
    thumb: str
    caption: str = ""

class Tribe(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    tags: List[str] = Field(default_factory=list)
    type: str = "public"
    description: str = ""
    avatar: str = "https://api.dicebear.com/7.x/shapes/svg?seed=tribe"
    ownerId: str
    members: List[str] = Field(default_factory=list)
    memberCount: int = 0
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class TribeCreate(BaseModel):
    name: str
    tags: List[str] = []
    type: str = "public"
    description: str = ""

class Comment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    postId: Optional[str] = None
    reelId: Optional[str] = None
    authorId: str
    text: str
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CommentCreate(BaseModel):
    text: str

class Message(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    fromId: str
    toId: str
    text: str
    read: bool = False
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class MessageCreate(BaseModel):
    text: str

class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    type: str  # post_like, tribe_join, order_ready, ticket_bought, dm
    payload: dict = Field(default_factory=dict)
    read: bool = False
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Venue(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    avatar: str = "https://api.dicebear.com/7.x/shapes/svg?seed=venue"
    location: str = ""
    rating: float = 4.5
    menuItems: List[dict] = Field(default_factory=list)
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Event(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    image: str = ""
    date: str = ""
    location: str = ""
    tiers: List[dict] = Field(default_factory=list)
    vibeMeter: int = 85
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Creator(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    displayName: str
    avatar: str = ""
    bio: str = ""
    items: List[dict] = Field(default_factory=list)
    followers: int = 0
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class WalletTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    type: str  # topup, withdraw, payment, refund
    amount: float
    status: str = "completed"
    description: str = ""
    metadata: dict = {}
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class TopUpRequest(BaseModel):
    amount: float

class PaymentRequest(BaseModel):
    amount: float
    venueId: str = None
    venueName: str = None
    description: str

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    venueId: str
    items: List[dict] = Field(default_factory=list)
    total: float = 0.0
    split: List[dict] = Field(default_factory=list)
    status: str = "pending"  # pending, paid, preparing, ready, completed
    paymentLink: Optional[str] = None
    razorpayOrderId: Optional[str] = None
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class OrderCreate(BaseModel):
    venueId: str
    items: List[dict]
    total: float
    split: List[dict] = []


# ===== NEW MODELS FOR ENHANCED FEATURES =====

class LoopCredit(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    amount: int
    type: str  # earn, spend
    source: str  # post, checkin, challenge, event, purchase
    description: str = ""
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CheckIn(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    venueId: str
    checkedInAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    checkedOutAt: Optional[str] = None
    status: str = "active"  # active, completed

class Offer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    venueId: str
    title: str
    description: str
    creditsRequired: int = 0
    validUntil: str
    claimLimit: int = 100
    claimedCount: int = 0
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class OfferClaim(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    offerId: str
    venueId: str
    qrCode: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "active"  # active, redeemed, expired
    claimedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    redeemedAt: Optional[str] = None

class Poll(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    postId: str
    question: str
    options: List[dict] = Field(default_factory=list)  # [{"id": "1", "text": "Option 1", "votes": 0}]
    totalVotes: int = 0
    votedBy: List[str] = Field(default_factory=list)
    endsAt: str
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Bookmark(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    postId: str
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class TribeChallenge(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tribeId: str
    title: str
    description: str
    reward: int  # Loop Credits
    startDate: str
    endDate: str
    participants: List[str] = Field(default_factory=list)
    completedBy: List[str] = Field(default_factory=list)
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class EventTicket(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    eventId: str
    userId: str
    qrCode: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tier: str = "General"
    status: str = "active"  # active, used, cancelled
    purchasedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    usedAt: Optional[str] = None

class UserInterest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    userId: str
    interests: List[str] = Field(default_factory=list)  # music, fitness, food, tech, art, etc.
    language: str = "en"  # en, hi, te
    onboardingComplete: bool = False

class UserAnalytics(BaseModel):
    model_config = ConfigDict(extra="ignore")
    userId: str
    totalCredits: int = 0
    totalPosts: int = 0
    totalCheckins: int = 0
    totalChallengesCompleted: int = 0
    vibeRank: int = 0
    tier: str = "Bronze"  # Bronze, Silver, Gold, Platinum
    lastUpdated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserConsent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    userId: str
    dataCollection: bool = False  # Required for app functionality
    personalizedAds: bool = False
    locationTracking: bool = False
    emailNotifications: bool = False
    pushNotifications: bool = False
    dataSharing: bool = False
    kycCompleted: bool = False
    aadhaarNumber: Optional[str] = None
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updatedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# Initialize Razorpay client
razorpay_key = os.environ.get('RAZORPAY_KEY', 'rzp_test_xxx')
razorpay_secret = os.environ.get('RAZORPAY_SECRET', 'rzp_secret_xxx')

class FriendRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    fromUserId: str
    toUserId: str
    status: str = "pending"  # pending, accepted, rejected
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class VibeRoom(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    category: str = "general"  # music, tech, gaming, lifestyle, business, etc.
    hostId: str
    hostName: str = ""
    moderators: List[str] = []
    participants: List[dict] = []  # [{userId, userName, avatar, joinedAt, isMuted}]
    maxParticipants: int = 50
    status: str = "active"  # active, ended
    isPrivate: bool = False
    tags: List[str] = []
    startedAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    endedAt: Optional[str] = None
    totalJoins: int = 0
    peakParticipants: int = 0

class RoomCreate(BaseModel):
    name: str
    description: str = ""
    category: str = "general"
    isPrivate: bool = False
    tags: List[str] = []

class RoomMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    roomId: str
    userId: str
    userName: str
    avatar: str = ""
    message: str
    type: str = "text"  # text, emoji, system
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class RoomAction(BaseModel):
    action: str  # kick, ban, handRaise, reaction
    targetUserId: str = None
    data: dict = {}

class RoomInvite(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    roomId: str
    fromUserId: str
    toUserId: str
    status: str = "pending"  # pending, accepted, declined
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Friendship(BaseModel):
    model_config = ConfigDict(extra="ignore")
    userId1: str
    userId2: str
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

# ===== NEW MODELS FOR FRIEND SYSTEM & DM =====

class UserBlock(BaseModel):
    model_config = ConfigDict(extra="ignore")
    blockerId: str
    blockedId: str
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserMute(BaseModel):
    model_config = ConfigDict(extra="ignore")
    muterId: str
    mutedId: str
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DMThread(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user1Id: str
    user2Id: str
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    lastMessageAt: Optional[str] = None

class DMMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    threadId: str
    senderId: str
    text: Optional[str] = None
    mediaUrl: Optional[str] = None
    mimeType: Optional[str] = None
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    editedAt: Optional[str] = None
    deletedAt: Optional[str] = None

class MessageRead(BaseModel):
    model_config = ConfigDict(extra="ignore")
    threadId: str
    userId: str
    lastReadMessageId: Optional[str] = None
    readAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

razorpay_client = razorpay.Client(auth=(razorpay_key, razorpay_secret))

# ===== JWT TOKEN UTILITIES =====

def create_access_token(user_id: str) -> str:
    """Create a JWT access token for a user"""
    expiration = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        'sub': user_id,
        'exp': expiration,
        'iat': datetime.now(timezone.utc)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

def verify_token(token: str) -> Optional[str]:
    """Verify a JWT token and return the user_id if valid"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get('sub')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to get the current authenticated user"""
    token = credentials.credentials
    user_id = verify_token(token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Get user from Google Sheets
    user = sheets_db.find_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

# ===== WEBSOCKET HELPERS =====

async def emit_to_user(user_id: str, event: str, data: dict):
    """Emit event to a specific user if they're connected"""
    if user_id in connected_clients:
        sid = connected_clients[user_id]
        await sio.emit(event, data, room=sid)
        logging.info(f"Emitted {event} to user {user_id}")

async def emit_to_thread(thread_id: str, event: str, data: dict, exclude_user: str = None):
    """Emit event to all users in a thread"""
    # Get thread participants
    thread = await db.dm_threads.find_one({"id": thread_id}, {"_id": 0})
    if thread:
        for user_id in [thread['user1Id'], thread['user2Id']]:
            if user_id != exclude_user:
                await emit_to_user(user_id, event, data)

def get_canonical_friend_order(user_a: str, user_b: str) -> tuple:
    """Return users in canonical order (lexicographic)"""
    return (user_a, user_b) if user_a < user_b else (user_b, user_a)

async def are_friends(user_a: str, user_b: str) -> bool:
    """Check if two users are friends"""
    u1, u2 = get_canonical_friend_order(user_a, user_b)
    friendship = await db.friendships.find_one({"userId1": u1, "userId2": u2}, {"_id": 0})
    return friendship is not None

async def is_blocked(blocker: str, blocked: str) -> bool:
    """Check if blocker has blocked blocked"""
    block = await db.user_blocks.find_one({"blockerId": blocker, "blockedId": blocked}, {"_id": 0})
    return block is not None

# ===== WEBSOCKET EVENT HANDLERS =====

@sio.event
async def connect(sid, environ, auth):
    """Handle client connection"""
    try:
        # Extract token from auth
        if not auth or 'token' not in auth:
            logging.warning(f"Connection rejected: no token provided")
            return False
        
        token = auth['token']
        user_id = verify_token(token)
        
        if not user_id:
            logging.warning(f"Connection rejected: invalid token")
            return False
        
        # Store connection
        connected_clients[user_id] = sid
        logging.info(f"User {user_id} connected with sid {sid}")
        
        # Join personal room
        await sio.enter_room(sid, f"user:{user_id}")
        
        return True
        
    except Exception as e:
        logging.error(f"Connection error: {e}")
        return False

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    try:
        # Find and remove user
        user_id = None
        for uid, client_sid in list(connected_clients.items()):
            if client_sid == sid:
                user_id = uid
                del connected_clients[uid]
                break
        
        if user_id:
            logging.info(f"User {user_id} disconnected")
    except Exception as e:
        logging.error(f"Disconnect error: {e}")

@sio.event
async def typing(sid, data):
    """Handle typing indicator"""
    try:
        thread_id = data.get('threadId')
        user_id = None
        
        # Find user_id from sid
        for uid, client_sid in connected_clients.items():
            if client_sid == sid:
                user_id = uid
                break
        
        if user_id and thread_id:
            await emit_to_thread(thread_id, 'typing', {
                'threadId': thread_id,
                'userId': user_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }, exclude_user=user_id)
    except Exception as e:
        logging.error(f"Typing event error: {e}")

# ===== AUTH ROUTES (REAL AUTHENTICATION WITH GOOGLE SHEETS) =====

@api_router.post("/auth/signup", response_model=dict)
async def signup(req: UserCreate):
    """
    Register a new user with email and password.
    User data is stored in Google Sheets (or demo mode).
    """
    try:
        # Check if handle already exists in MongoDB
        existing_handle = await db.users.find_one({"handle": req.handle}, {"_id": 0})
        if existing_handle:
            raise HTTPException(status_code=400, detail=f"Username '@{req.handle}' is already taken. Please choose a different username.")
        
        # Create user in Google Sheets
        user = sheets_db.create_user(
            name=req.name,
            email=req.email,
            password=req.password
        )
        
        # Also create user in MongoDB for app data (posts, tribes, etc.)
        mongo_user = User(
            id=user['user_id'],
            handle=req.handle,
            name=req.name,
            email=req.email,
            avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={req.handle}"
        )
        doc = mongo_user.model_dump()
        await db.users.insert_one(doc)
        
        # Generate JWT token
        token = create_access_token(user['user_id'])
        
        return {
            "token": token,
            "user": {
                "id": user['user_id'],
                "handle": req.handle,
                "name": user['name'],
                "email": user['email'],
                "avatar": mongo_user.avatar
            }
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.get("/auth/check-handle/{handle}")
async def check_handle_availability(handle: str):
    """Check if a username/handle is available"""
    existing = await db.users.find_one({"handle": handle}, {"_id": 0})
    return {
        "available": existing is None,
        "handle": handle
    }

@api_router.post("/auth/login", response_model=dict)
async def login(req: LoginRequest):
    """
    Login with email and password.
    Returns a JWT token on successful authentication.
    """
    # Verify credentials with Google Sheets
    user = sheets_db.verify_password(req.email, req.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Get or create user data in MongoDB for app functionality
    mongo_user = await db.users.find_one({"id": user['user_id']}, {"_id": 0})
    
    if not mongo_user:
        # Create user in MongoDB if doesn't exist
        handle = user['email'].split('@')[0]
        new_mongo_user = User(
            id=user['user_id'],
            handle=handle,
            name=user['name'],
            email=user['email'],
            avatar=f"https://api.dicebear.com/7.x/avataaars/svg?seed={handle}"
        )
        doc = new_mongo_user.model_dump()
        await db.users.insert_one(doc)
        mongo_user = doc
    
    # Generate JWT token
    token = create_access_token(user['user_id'])
    
    return {
        "token": token,
        "user": {
            "id": user['user_id'],
            "handle": mongo_user.get('handle', user['email'].split('@')[0]),
            "name": user['name'],
            "email": user['email'],
            "avatar": mongo_user.get('avatar', f"https://api.dicebear.com/7.x/avataaars/svg?seed={user['email']}")
        }
    }
    
    return {
        "token": token,
        "user": {
            "id": user['user_id'],
            "handle": mongo_user.get('handle', user['email'].split('@')[0]),
            "name": user['name'],
            "email": user['email']
        }
    }

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get the current authenticated user's profile.
    Requires valid JWT token.
    """
    # Get additional user data from MongoDB
    mongo_user = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0})
    
    if not mongo_user:
        # If not in MongoDB, return basic info from Google Sheets
        return {
            "id": current_user['user_id'],
            "name": current_user['name'],
            "email": current_user['email']
        }
    
    return mongo_user

# ===== USER ROUTES =====

@api_router.get("/users/{userId}", response_model=User)
async def get_user(userId: str):
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.get("/users/{userId}/profile")
async def get_user_profile(userId: str, currentUserId: str = None):
    """Get user profile with posts, followers, and following counts"""
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's posts
    posts = await db.posts.find({"authorId": userId}, {"_id": 0}).sort("createdAt", -1).to_list(100)
    for post in posts:
        post["author"] = user
    
    # Count followers (users who are friends with this user)
    followers_count = 0
    following_count = 0
    
    # Count friendships where this user is user1
    count1 = await db.friendships.count_documents({"userId1": userId})
    # Count friendships where this user is user2
    count2 = await db.friendships.count_documents({"userId2": userId})
    
    # Total friends count (each friendship is bidirectional)
    friends_count = count1 + count2
    
    # For now, followers = following = friends count (simplified friend model)
    followers_count = friends_count
    following_count = friends_count
    
    # Check relationship status if currentUserId provided
    relationship_status = None
    if currentUserId and currentUserId != userId:
        # Check if friends
        is_friend = await are_friends(currentUserId, userId)
        if is_friend:
            relationship_status = "friends"
        else:
            # Check friend requests
            sent_request = await db.friend_requests.find_one({
                "fromUserId": currentUserId,
                "toUserId": userId,
                "status": "pending"
            }, {"_id": 0})
            
            received_request = await db.friend_requests.find_one({
                "fromUserId": userId,
                "toUserId": currentUserId,
                "status": "pending"
            }, {"_id": 0})
            
            if sent_request:
                relationship_status = "pending_sent"
            elif received_request:
                relationship_status = "pending_received"
            else:
                relationship_status = None
    
    return {
        "user": user,
        "posts": posts,
        "followersCount": followers_count,
        "followingCount": following_count,
        "postsCount": len(posts),
        "relationshipStatus": relationship_status
    }

@api_router.put("/users/{userId}")
async def update_user(userId: str, data: dict):
    """Update user profile"""
    allowed_fields = ["name", "handle", "bio", "avatar"]
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    result = await db.users.update_one(
        {"id": userId},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "message": "Profile updated"}

@api_router.get("/users/{userId}/settings")
async def get_user_settings(userId: str):
    """Get user settings"""
    settings = await db.user_settings.find_one({"userId": userId}, {"_id": 0})
    if not settings:
        # Return default settings
        return {
            "accountPrivate": False,
            "showOnlineStatus": True,
            "allowMessagesFrom": "everyone",
            "showActivity": True,
            "allowTagging": True,
            "showStories": True,
            "emailNotifications": True,
            "pushNotifications": True,
            "likeNotifications": True,
            "commentNotifications": True,
            "followNotifications": True,
            "messageNotifications": True,
            "darkMode": False
        }
    return settings

@api_router.put("/users/{userId}/settings")
async def update_user_settings(userId: str, settings: dict):
    """Update user settings"""
    settings["userId"] = userId
    
    await db.user_settings.update_one(
        {"userId": userId},
        {"$set": settings},
        upsert=True
    )
    
    return {"success": True, "message": "Settings saved"}

@api_router.get("/users/{userId}/blocked")
async def get_blocked_users(userId: str):
    """Get list of blocked users"""
    blocks = await db.user_blocks.find({"blockerId": userId}, {"_id": 0}).to_list(None)
    
    blocked_users = []
    for block in blocks:
        user = await db.users.find_one({"id": block["blockedId"]}, {"_id": 0})
        if user:
            blocked_users.append(user)
    
    return blocked_users

@api_router.delete("/users/{userId}/block/{blockedUserId}")
async def unblock_user(userId: str, blockedUserId: str):
    """Unblock a user"""
    result = await db.user_blocks.delete_one({
        "blockerId": userId,
        "blockedId": blockedUserId
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Block not found")
    
    return {"success": True, "message": "User unblocked"}

@api_router.post("/auth/change-password")
async def change_password(data: dict):
    """Change user password"""
    userId = data.get("userId")
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")
    
    # Verify current password with Google Sheets DB
    user = sheets_db.find_user_by_id(userId)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not sheets_db.verify_password(user.get("email"), current_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    
    # Update password in Google Sheets
    sheets_db.update_user_password(user.get("email"), new_password)
    
    return {"success": True, "message": "Password changed successfully"}

@api_router.get("/search")
async def search_all(q: str, currentUserId: str = None, limit: int = 20):
    """Global search for users, posts, tribes, venues, events"""
    if not q or len(q) < 2:
        return {"users": [], "posts": [], "tribes": [], "venues": [], "events": []}
    
    query_pattern = {"$regex": q, "$options": "i"}
    
    # Search users
    users = await db.users.find({
        "$or": [
            {"name": query_pattern},
            {"handle": query_pattern}
        ]
    }, {"_id": 0}).limit(limit).to_list(limit)
    
    # Enrich users with friend status if currentUserId provided
    if currentUserId:
        for user in users:
            user["isFriend"] = await are_friends(currentUserId, user["id"])
            user["isBlocked"] = await is_blocked(currentUserId, user["id"])
    
    # Search posts
    posts = await db.posts.find({
        "text": query_pattern
    }, {"_id": 0}).sort("createdAt", -1).limit(limit).to_list(limit)
    
    for post in posts:
        author = await db.users.find_one({"id": post["authorId"]}, {"_id": 0})
        post["author"] = author
    
    # Search tribes
    tribes = await db.tribes.find({
        "$or": [
            {"name": query_pattern},
            {"description": query_pattern}
        ]
    }, {"_id": 0}).limit(limit).to_list(limit)
    
    # Search venues
    venues = await db.venues.find({
        "$or": [
            {"name": query_pattern},
            {"description": query_pattern},
            {"location": query_pattern}
        ]
    }, {"_id": 0}).limit(limit).to_list(limit)
    
    # Search events
    events = await db.events.find({
        "$or": [
            {"name": query_pattern},
            {"description": query_pattern},
            {"venue": query_pattern}
        ]
    }, {"_id": 0}).limit(limit).to_list(limit)
    
    return {
        "users": users,
        "posts": posts,
        "tribes": tribes,
        "venues": venues,
        "events": events
    }

# ===== POST ROUTES (TIMELINE) =====

@api_router.get("/posts")
async def get_posts(limit: int = 50):
    posts = await db.posts.find({}, {"_id": 0}).sort("createdAt", -1).to_list(limit)
    # Enrich with author data
    for post in posts:
        author = await db.users.find_one({"id": post["authorId"]}, {"_id": 0})
        post["author"] = author if author else None
    return posts

@api_router.post("/posts")
async def create_post(post: PostCreate, authorId: str):
    post_obj = Post(authorId=authorId, **post.model_dump())
    doc = post_obj.model_dump()
    result = await db.posts.insert_one(doc)
    # Remove _id from doc before returning
    doc.pop('_id', None)
    # Enrich with author
    author = await db.users.find_one({"id": authorId}, {"_id": 0})
    doc["author"] = author
    return doc

@api_router.post("/posts/{postId}/like")
async def toggle_like_post(postId: str, userId: str):
    post = await db.posts.find_one({"id": postId}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    liked_by = post.get("likedBy", [])
    stats = post.get("stats", {"likes": 0, "quotes": 0, "reposts": 0, "replies": 0})
    
    if userId in liked_by:
        liked_by.remove(userId)
        stats["likes"] = max(0, stats["likes"] - 1)
        action = "unliked"
    else:
        liked_by.append(userId)
        stats["likes"] = stats["likes"] + 1
        action = "liked"
        
        # Create notification for post author
        if post["authorId"] != userId:
            liker = await db.users.find_one({"id": userId}, {"_id": 0})
            notification = Notification(
                userId=post["authorId"],
                type="like",
                content=f"{liker.get('name', 'Someone')} liked your post",
                link=f"/posts/{postId}"
            )
            await db.notifications.insert_one(notification.model_dump())
    
    await db.posts.update_one({"id": postId}, {"$set": {"likedBy": liked_by, "stats": stats}})
    return {"action": action, "likes": stats["likes"]}

@api_router.post("/posts/{postId}/repost")
async def toggle_repost(postId: str, userId: str):
    post = await db.posts.find_one({"id": postId}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    reposted_by = post.get("repostedBy", [])
    stats = post.get("stats", {"likes": 0, "quotes": 0, "reposts": 0, "replies": 0})
    
    if userId in reposted_by:
        reposted_by.remove(userId)
        stats["reposts"] = max(0, stats["reposts"] - 1)
        action = "unreposted"
    else:
        reposted_by.append(userId)
        stats["reposts"] = stats["reposts"] + 1
        action = "reposted"
    
    await db.posts.update_one({"id": postId}, {"$set": {"repostedBy": reposted_by, "stats": stats}})
    return {"action": action, "reposts": stats["reposts"]}

@api_router.get("/posts/{postId}/comments")
async def get_post_comments(postId: str):
    comments = await db.comments.find({"postId": postId}, {"_id": 0}).sort("createdAt", -1).to_list(100)
    for comment in comments:
        author = await db.users.find_one({"id": comment["authorId"]}, {"_id": 0})
        comment["author"] = author

@api_router.delete("/posts/{postId}")
async def delete_post(postId: str):
    """Delete a post"""
    result = await db.posts.delete_one({"id": postId})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"success": True, "message": "Post deleted"}

    return comments

@api_router.post("/posts/{postId}/comments")
async def create_post_comment(postId: str, comment: CommentCreate, authorId: str):
    comment_obj = Comment(postId=postId, authorId=authorId, text=comment.text)
    doc = comment_obj.model_dump()
    result = await db.comments.insert_one(doc)
    doc.pop('_id', None)
    
    # Update post reply count
    await db.posts.update_one({"id": postId}, {"$inc": {"stats.replies": 1}})
    
    author = await db.users.find_one({"id": authorId}, {"_id": 0})
    doc["author"] = author
    return doc

# ===== REEL ROUTES (VIBEZONE) =====

@api_router.get("/reels")
async def get_reels(limit: int = 50):
    """Get all reels for VibeZone."""
    cursor = db.reels.find().sort("createdAt", -1).limit(limit)
    reels = await cursor.to_list(length=limit)
    for reel in reels:
        reel["_id"] = str(reel["_id"])
        # Add author info
        if "authorId" in reel:
            author = await db.users.find_one({"id": reel["authorId"]})
            if author:
                reel["author"] = {
                    "id": author["id"],
                    "handle": author["handle"],
                    "name": author["name"],
                    "avatar": author.get("avatar", "")
                }
    return reels

@api_router.get("/music/search")
async def search_music(q: str, limit: int = 10):
    """Mock JioSaavn-like search returning preview streams only (no downloads)."""
    sample = [
        {
            "id": f"mock-{i}",
            "title": f"{q.title()} Track {i+1}",
            "artists": ["Mock Artist"],
            "artwork": f"https://picsum.photos/seed/{q}{i}/200/200",
            "duration": 30,
            "previewUrl": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
        }
        for i in range(min(limit, 10))
    ]
    return {"items": sample}


    reels = await db.reels.find({}, {"_id": 0}).sort("createdAt", -1).to_list(limit)
    for reel in reels:
        author = await db.users.find_one({"id": reel["authorId"]}, {"_id": 0})
        reel["author"] = author if author else None
    return reels

@api_router.post("/reels")
async def create_reel(reel: ReelCreate, authorId: str):
    reel_obj = Reel(authorId=authorId, **reel.model_dump())
    doc = reel_obj.model_dump()
    result = await db.reels.insert_one(doc)
    doc.pop('_id', None)
    author = await db.users.find_one({"id": authorId}, {"_id": 0})
    doc["author"] = author
    return doc

@api_router.post("/reels/{reelId}/like")
async def toggle_like_reel(reelId: str, userId: str):
    reel = await db.reels.find_one({"id": reelId}, {"_id": 0})
    if not reel:
        raise HTTPException(status_code=404, detail="Reel not found")
    
    liked_by = reel.get("likedBy", [])
    stats = reel.get("stats", {"views": 0, "likes": 0, "comments": 0})
    
    if userId in liked_by:
        liked_by.remove(userId)
        stats["likes"] = max(0, stats["likes"] - 1)
        action = "unliked"
    else:
        liked_by.append(userId)
        stats["likes"] = stats["likes"] + 1
        action = "liked"
    
    await db.reels.update_one({"id": reelId}, {"$set": {"likedBy": liked_by, "stats": stats}})
    return {"action": action, "likes": stats["likes"]}

@api_router.post("/reels/{reelId}/view")
async def increment_reel_view(reelId: str):
    await db.reels.update_one({"id": reelId}, {"$inc": {"stats.views": 1}})
    return {"success": True}

@api_router.get("/reels/{reelId}/comments")
async def get_reel_comments(reelId: str):
    comments = await db.comments.find({"reelId": reelId}, {"_id": 0}).sort("createdAt", -1).to_list(100)
    for comment in comments:
        author = await db.users.find_one({"id": comment["authorId"]}, {"_id": 0})
        comment["author"] = author
    return comments

@api_router.post("/reels/{reelId}/comments")
async def create_reel_comment(reelId: str, comment: CommentCreate, authorId: str):
    comment_obj = Comment(reelId=reelId, authorId=authorId, text=comment.text)
    doc = comment_obj.model_dump()
    result = await db.comments.insert_one(doc)
    doc.pop('_id', None)
    
    await db.reels.update_one({"id": reelId}, {"$inc": {"stats.comments": 1}})
    
    author = await db.users.find_one({"id": authorId}, {"_id": 0})
    doc["author"] = author
    return doc

# ===== TRIBE ROUTES =====

@api_router.get("/tribes")
async def get_tribes(limit: int = 50):
    tribes = await db.tribes.find({}, {"_id": 0}).sort("memberCount", -1).to_list(limit)
    return tribes

@api_router.get("/tribes/{tribeId}")
async def get_tribe(tribeId: str):
    tribe = await db.tribes.find_one({"id": tribeId}, {"_id": 0})
    if not tribe:
        raise HTTPException(status_code=404, detail="Tribe not found")
    return tribe

@api_router.post("/tribes")
async def create_tribe(tribe: TribeCreate, ownerId: str):
    tribe_obj = Tribe(ownerId=ownerId, members=[ownerId], memberCount=1, **tribe.model_dump())
    doc = tribe_obj.model_dump()
    result = await db.tribes.insert_one(doc)
    doc.pop('_id', None)
    return doc

@api_router.post("/tribes/{tribeId}/join")
async def join_tribe(tribeId: str, userId: str):
    tribe = await db.tribes.find_one({"id": tribeId}, {"_id": 0})
    if not tribe:
        raise HTTPException(status_code=404, detail="Tribe not found")
    
    members = tribe.get("members", [])
    if userId in members:
        return {"message": "Already a member", "memberCount": len(members)}
    
    members.append(userId)
    await db.tribes.update_one({"id": tribeId}, {"$set": {"members": members, "memberCount": len(members)}})
    return {"message": "Joined", "memberCount": len(members)}

@api_router.post("/tribes/{tribeId}/leave")
async def leave_tribe(tribeId: str, userId: str):
    tribe = await db.tribes.find_one({"id": tribeId}, {"_id": 0})
    if not tribe:
        raise HTTPException(status_code=404, detail="Tribe not found")
    
    members = tribe.get("members", [])
    if userId not in members:
        return {"message": "Not a member", "memberCount": len(members)}
    
    members.remove(userId)
    await db.tribes.update_one({"id": tribeId}, {"$set": {"members": members, "memberCount": len(members)}})
    return {"message": "Left", "memberCount": len(members)}

@api_router.get("/tribes/{tribeId}/posts")
async def get_tribe_posts(tribeId: str, limit: int = 50):
    # Mock: return posts with tribe tag or from tribe members
    tribe = await db.tribes.find_one({"id": tribeId}, {"_id": 0})
    if not tribe:
        raise HTTPException(status_code=404, detail="Tribe not found")
    
    posts = await db.posts.find({"authorId": {"$in": tribe.get("members", [])}}, {"_id": 0}).sort("createdAt", -1).to_list(limit)
    for post in posts:
        author = await db.users.find_one({"id": post["authorId"]}, {"_id": 0})
        post["author"] = author
    return posts

# ===== DAILY.CO INTEGRATION ROUTES =====

@api_router.post("/daily/rooms")
async def create_daily_room(userId: str, roomName: str):
    """Create a Daily.co room for real-time audio"""
    import httpx
    
    daily_api_key = os.environ.get('DAILY_API_KEY')
    if not daily_api_key:
        raise HTTPException(status_code=500, detail="Daily API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.daily.co/v1/rooms",
                json={
                    "properties": {
                        "enable_chat": False,
                        "enable_screenshare": False,
                        "start_video_off": True,
                        "start_audio_off": False,
                        "owner_only_broadcast": False,
                        "exp": int(datetime.now(timezone.utc).timestamp()) + 3600  # 1 hour
                    }
                },
                headers={
                    "Authorization": f"Bearer {daily_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to create Daily room: {response.text}"
                )
            
            daily_room = response.json()
            return {
                "dailyRoomUrl": daily_room.get("url"),
                "dailyRoomName": daily_room.get("name"),
                "success": True
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Daily room: {str(e)}")

@api_router.post("/daily/token")
async def create_daily_token(roomName: str, userName: str, isOwner: bool = False):
    """Create a Daily.co meeting token for controlled access"""
    import httpx
    
    daily_api_key = os.environ.get('DAILY_API_KEY')
    if not daily_api_key:
        raise HTTPException(status_code=500, detail="Daily API key not configured")
    
    try:
        token_properties = {
            "room_name": roomName,
            "user_name": userName,
            "is_owner": isOwner,
            "start_audio_off": False,
            "start_video_off": True,
            "exp": int(datetime.now(timezone.utc).timestamp()) + 3600
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.daily.co/v1/meeting-tokens",
                json={"properties": token_properties},
                headers={
                    "Authorization": f"Bearer {daily_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to create token: {response.text}"
                )
            
            token_data = response.json()
            return {
                "token": token_data.get("token"),
                "success": True
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating token: {str(e)}")

# ===== VIBE ROOMS (VOICE ROOMS) ROUTES =====

@api_router.post("/rooms")
async def create_room(room: RoomCreate, userId: str):
    """Create a new Vibe Room with Daily.co integration"""
    import httpx
    
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create Daily.co room first
    daily_api_key = os.environ.get('DAILY_API_KEY')
    daily_room_url = None
    daily_room_name = None
    
    if daily_api_key:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.daily.co/v1/rooms",
                    json={
                        "properties": {
                            "enable_chat": False,
                            "enable_screenshare": False,
                            "start_video_off": True,
                            "start_audio_off": False,
                            "exp": int(datetime.now(timezone.utc).timestamp()) + 3600
                        }
                    },
                    headers={
                        "Authorization": f"Bearer {daily_api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    daily_room = response.json()
                    daily_room_url = daily_room.get("url")
                    daily_room_name = daily_room.get("name")
        except Exception as e:
            print(f"Failed to create Daily room: {e}")
    
    new_room = VibeRoom(
        name=room.name,
        description=room.description,
        category=room.category,
        hostId=userId,
        hostName=user.get("name", "Unknown"),
        moderators=[userId],
        isPrivate=room.isPrivate,
        tags=room.tags,
        participants=[{
            "userId": userId,
            "userName": user.get("name", "Unknown"),
            "avatar": user.get("avatar", ""),
            "joinedAt": datetime.now(timezone.utc).isoformat(),
            "isMuted": False,
            "isHost": True
        }],
        totalJoins=1,
        peakParticipants=1
    )
    
    room_dict = new_room.model_dump()
    if daily_room_url:
        room_dict["dailyRoomUrl"] = daily_room_url
        room_dict["dailyRoomName"] = daily_room_name
    
    await db.vibe_rooms.insert_one(room_dict)
    return room_dict

@api_router.get("/rooms")
async def get_active_rooms(category: str = None, limit: int = 50):
    """Get list of active Vibe Rooms"""
    query = {"status": "active"}
    if category and category != "all":
        query["category"] = category
    
    rooms = await db.vibe_rooms.find(query, {"_id": 0}).sort("startedAt", -1).to_list(limit)
    return rooms

@api_router.get("/rooms/{roomId}")
async def get_room(roomId: str):
    """Get specific room details"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@api_router.post("/rooms/{roomId}/join")
async def join_room(roomId: str, userId: str):
    """Join a Vibe Room"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.get("status") != "active":
        raise HTTPException(status_code=400, detail="Room is not active")
    
    # Check if already in room
    participants = room.get("participants", [])
    if any(p["userId"] == userId for p in participants):
        return {"message": "Already in room", "room": room}
    
    # Check max participants
    if len(participants) >= room.get("maxParticipants", 50):
        raise HTTPException(status_code=400, detail="Room is full")
    
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add participant
    new_participant = {
        "userId": userId,
        "userName": user.get("name", "Unknown"),
        "avatar": user.get("avatar", ""),
        "joinedAt": datetime.now(timezone.utc).isoformat(),
        "isMuted": False,
        "isHost": False
    }
    participants.append(new_participant)
    
    # Update peak participants
    peak = max(room.get("peakParticipants", 0), len(participants))
    
    await db.vibe_rooms.update_one(
        {"id": roomId},
        {
            "$set": {
                "participants": participants,
                "peakParticipants": peak
            },
            "$inc": {"totalJoins": 1}
        }
    )
    
    # Emit WebSocket event
    room["participants"] = participants
    room["peakParticipants"] = peak
    
    return {"message": "Joined room", "room": room, "participant": new_participant}

@api_router.post("/rooms/{roomId}/leave")
async def leave_room(roomId: str, userId: str):
    """Leave a Vibe Room"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    participants = room.get("participants", [])
    participants = [p for p in participants if p["userId"] != userId]
    
    # If host leaves and there are participants, assign new host
    if room.get("hostId") == userId and len(participants) > 0:
        new_host = participants[0]
        await db.vibe_rooms.update_one(
            {"id": roomId},
            {
                "$set": {
                    "hostId": new_host["userId"],
                    "hostName": new_host["userName"],
                    "participants": participants
                }
            }
        )
        return {"message": "Left room, host transferred", "newHostId": new_host["userId"]}
    
    # If no participants left, end room
    if len(participants) == 0:
        await db.vibe_rooms.update_one(
            {"id": roomId},
            {
                "$set": {
                    "status": "ended",
                    "endedAt": datetime.now(timezone.utc).isoformat(),
                    "participants": []
                }
            }
        )
        return {"message": "Room ended"}
    
    await db.vibe_rooms.update_one(
        {"id": roomId},
        {"$set": {"participants": participants}}
    )
    
    return {"message": "Left room", "participantCount": len(participants)}

@api_router.post("/rooms/{roomId}/end")
async def end_room(roomId: str, userId: str):
    """End a Vibe Room (host only)"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.get("hostId") != userId:
        raise HTTPException(status_code=403, detail="Only host can end room")
    
    await db.vibe_rooms.update_one(
        {"id": roomId},
        {
            "$set": {
                "status": "ended",
                "endedAt": datetime.now(timezone.utc).isoformat(),
                "participants": []
            }
        }
    )
    
    return {"message": "Room ended"}

@api_router.post("/rooms/{roomId}/mute")
async def toggle_mute(roomId: str, userId: str, targetUserId: str = None):
    """Toggle mute for self or others (moderator)"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    target = targetUserId or userId
    
    # Check if user is moderator when muting others
    if targetUserId and userId not in room.get("moderators", []):
        raise HTTPException(status_code=403, detail="Only moderators can mute others")
    
    participants = room.get("participants", [])
    for p in participants:
        if p["userId"] == target:
            p["isMuted"] = not p.get("isMuted", False)
            break
    
    await db.vibe_rooms.update_one(
        {"id": roomId},
        {"$set": {"participants": participants}}
    )
    
    return {"message": "Mute toggled", "participants": participants}

@api_router.post("/rooms/{roomId}/promote")
async def promote_moderator(roomId: str, userId: str, targetUserId: str):
    """Promote user to moderator (host only)"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if room.get("hostId") != userId:
        raise HTTPException(status_code=403, detail="Only host can promote moderators")
    
    moderators = room.get("moderators", [])
    if targetUserId not in moderators:
        moderators.append(targetUserId)
    
    await db.vibe_rooms.update_one(
        {"id": roomId},
        {"$set": {"moderators": moderators}}
    )
    
    return {"message": "User promoted to moderator", "moderators": moderators}

@api_router.post("/rooms/{roomId}/kick")
async def kick_user(roomId: str, userId: str, targetUserId: str):
    """Kick user from room (moderator/host only)"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if userId not in room.get("moderators", []):
        raise HTTPException(status_code=403, detail="Only moderators can kick users")
    
    # Remove participant
    participants = room.get("participants", [])
    participants = [p for p in participants if p["userId"] != targetUserId]
    
    await db.vibe_rooms.update_one(
        {"id": roomId},
        {"$set": {"participants": participants}}
    )
    
    # Log action
    message = RoomMessage(
        roomId=roomId,
        userId="system",
        userName="System",
        message=f"User was removed from the room",
        type="system"
    )
    await db.room_messages.insert_one(message.model_dump())
    
    return {"message": "User kicked", "participants": participants}

@api_router.post("/rooms/{roomId}/handRaise")
async def toggle_hand_raise(roomId: str, userId: str):
    """Toggle hand raise for user"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    participants = room.get("participants", [])
    for p in participants:
        if p["userId"] == userId:
            p["handRaised"] = not p.get("handRaised", False)
            break
    
    await db.vibe_rooms.update_one(
        {"id": roomId},
        {"$set": {"participants": participants}}
    )
    
    return {"message": "Hand raise toggled", "participants": participants}

@api_router.post("/rooms/{roomId}/reaction")
async def add_reaction(roomId: str, userId: str, emoji: str):
    """Add emoji reaction in room"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Get user info
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    
    # Add reaction message
    message = RoomMessage(
        roomId=roomId,
        userId=userId,
        userName=user.get("name", "User"),
        avatar=user.get("avatar", ""),
        message=emoji,
        type="emoji"
    )
    await db.room_messages.insert_one(message.model_dump())
    
    return {"message": "Reaction added"}

# ===== ROOM CHAT ROUTES =====

@api_router.post("/rooms/{roomId}/messages")
async def send_room_message(roomId: str, userId: str, message: str):
    """Send chat message in room"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if user is in room
    participants = room.get("participants", [])
    if not any(p["userId"] == userId for p in participants):
        raise HTTPException(status_code=403, detail="Not in room")
    
    # Get user info
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    
    # Create message
    room_message = RoomMessage(
        roomId=roomId,
        userId=userId,
        userName=user.get("name", "User"),
        avatar=user.get("avatar", ""),
        message=message,
        type="text"
    )
    await db.room_messages.insert_one(room_message.model_dump())
    
    return room_message

@api_router.get("/rooms/{roomId}/messages")
async def get_room_messages(roomId: str, limit: int = 50):
    """Get chat messages for room"""
    messages = await db.room_messages.find(
        {"roomId": roomId},
        {"_id": 0}
    ).sort("createdAt", -1).limit(limit).to_list(limit)
    
    # Reverse to show oldest first
    return list(reversed(messages))

@api_router.delete("/rooms/{roomId}/messages/{messageId}")
async def delete_room_message(roomId: str, messageId: str, userId: str):
    """Delete chat message (moderator/host only)"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    if userId not in room.get("moderators", []):
        raise HTTPException(status_code=403, detail="Only moderators can delete messages")
    
    await db.room_messages.delete_one({"id": messageId, "roomId": roomId})
    
    return {"message": "Message deleted"}

# ===== ROOM INVITATION ROUTES =====

@api_router.post("/rooms/{roomId}/invite")
async def invite_to_room(roomId: str, fromUserId: str, toUserId: str):
    """Invite a friend to a Vibe Room"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # Check if user is in room
    if not any(p["userId"] == fromUserId for p in room.get("participants", [])):
        raise HTTPException(status_code=403, detail="Must be in room to invite")
    
    # Get users
    from_user = await db.users.find_one({"id": fromUserId}, {"_id": 0})
    to_user = await db.users.find_one({"id": toUserId}, {"_id": 0})
    
    if not to_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create invite
    invite = RoomInvite(
        roomId=roomId,
        fromUserId=fromUserId,
        toUserId=toUserId,
        status="pending"
    )
    await db.room_invites.insert_one(invite.model_dump())
    
    # Create notification
    notification = {
        "id": str(uuid.uuid4()),
        "userId": toUserId,
        "type": "room_invite",
        "fromUserId": fromUserId,
        "fromUserName": from_user.get("name", "Someone"),
        "roomId": roomId,
        "roomName": room.get("name", "a room"),
        "message": f"{from_user.get('name', 'Someone')} invited you to join {room.get('name', 'a room')}",
        "read": False,
        "createdAt": datetime.now(timezone.utc).isoformat()
    }
    await db.notifications.insert_one(notification)
    
    return {"message": "Invitation sent", "inviteId": invite.id}

@api_router.get("/rooms/invites/{userId}")
async def get_room_invites(userId: str):
    """Get all room invitations for user"""
    invites = await db.room_invites.find(
        {"toUserId": userId, "status": "pending"},
        {"_id": 0}
    ).to_list(None)
    
    # Enrich with room and user info
    enriched = []
    for invite in invites:
        room = await db.vibe_rooms.find_one({"id": invite["roomId"]}, {"_id": 0})
        from_user = await db.users.find_one({"id": invite["fromUserId"]}, {"_id": 0})
        
        if room and from_user:
            enriched.append({
                **invite,
                "roomName": room.get("name"),
                "roomCategory": room.get("category"),
                "fromUserName": from_user.get("name"),
                "fromUserAvatar": from_user.get("avatar", "")
            })
    
    return enriched

@api_router.post("/rooms/invites/{inviteId}/accept")
async def accept_room_invite(inviteId: str, userId: str):
    """Accept room invitation"""
    invite = await db.room_invites.find_one({"id": inviteId}, {"_id": 0})
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    
    if invite["toUserId"] != userId:
        raise HTTPException(status_code=403, detail="Not your invite")
    
    # Update invite status
    await db.room_invites.update_one(
        {"id": inviteId},
        {"$set": {"status": "accepted"}}
    )
    
    # Return room details
    room = await db.vibe_rooms.find_one({"id": invite["roomId"]}, {"_id": 0})
    return {"message": "Invite accepted", "room": room}

@api_router.post("/rooms/invites/{inviteId}/decline")
async def decline_room_invite(inviteId: str, userId: str):
    """Decline room invitation"""
    invite = await db.room_invites.find_one({"id": inviteId}, {"_id": 0})
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    
    if invite["toUserId"] != userId:
        raise HTTPException(status_code=403, detail="Not your invite")
    
    await db.room_invites.update_one(
        {"id": inviteId},
        {"$set": {"status": "declined"}}
    )
    
    return {"message": "Invite declined"}

@api_router.get("/rooms/{roomId}/share-link")
async def get_room_share_link(roomId: str):
    """Get shareable link for room"""
    room = await db.vibe_rooms.find_one({"id": roomId}, {"_id": 0})
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    # In production, use actual domain
    share_link = f"https://loopync.app/rooms/{roomId}"
    
    return {
        "shareLink": share_link,
        "roomName": room.get("name"),
        "roomId": roomId
    }

# ===== SEED DATA ROUTE =====

@api_router.post("/seed")
async def seed_data():
    # Clear existing data
    await db.users.delete_many({})
    await db.posts.delete_many({})
    await db.reels.delete_many({})
    await db.tribes.delete_many({})
    await db.comments.delete_many({})
    await db.wallet_transactions.delete_many({})
    await db.messages.delete_many({})
    await db.notifications.delete_many({})
    await db.venues.delete_many({})
    await db.events.delete_many({})
    await db.creators.delete_many({})
    
    # Seed users
    users = [
        {"id": "u1", "handle": "vibekween", "name": "Priya Sharma", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=priya", "bio": "Free speech advocate | Coffee addict ☕", "kycTier": 2, "walletBalance": 500.0, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u2", "handle": "techbro_raj", "name": "Raj Malhotra", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=raj", "bio": "Building in public 🚀", "kycTier": 1, "walletBalance": 1000.0, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u3", "handle": "artsy_soul", "name": "Ananya Reddy", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=ananya", "bio": "Digital artist | Vibe curator 🎨", "kycTier": 1, "walletBalance": 750.0, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u4", "handle": "crypto_maya", "name": "Maya Patel", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=maya", "bio": "Web3 enthusiast | HODL 💎", "kycTier": 3, "walletBalance": 2500.0, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u5", "handle": "foodie_sahil", "name": "Sahil Khan", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=sahil", "bio": "Food blogger | Mumbai's best eats 🍕", "kycTier": 1, "walletBalance": 300.0, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "demo_user", "handle": "demo", "name": "Demo User", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=demo", "bio": "Testing Loopync! 🎉", "kycTier": 1, "walletBalance": 1500.0, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.users.insert_many(users)
    
    # Seed posts
    posts = [
        {"id": "p1", "authorId": "u1", "text": "Free speech doesn't mean freedom from consequences, but it does mean freedom to speak. Let's normalize respectful disagreement! 🗣️", "media": None, "audience": "public", "stats": {"likes": 42, "quotes": 5, "reposts": 12, "replies": 8}, "likedBy": ["u2", "u3"], "repostedBy": ["u4"], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "p2", "authorId": "u2", "text": "Just launched my new side project! Built with React + FastAPI. Ship fast, iterate faster 🚀", "media": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800", "audience": "public", "stats": {"likes": 89, "quotes": 3, "reposts": 22, "replies": 15}, "likedBy": ["u1", "u3", "u5"], "repostedBy": [], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "p3", "authorId": "u3", "text": "New artwork drop! Exploring neon aesthetics and cyber themes. What do you think? 💫", "media": "https://images.unsplash.com/photo-1634973357973-f2ed2657db3c?w=800", "audience": "public", "stats": {"likes": 156, "quotes": 8, "reposts": 34, "replies": 22}, "likedBy": ["u1", "u2", "u4", "u5"], "repostedBy": ["u1"], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "p4", "authorId": "u4", "text": "The future is decentralized. India needs more Web3 builders. Who's with me? 🌐", "media": None, "audience": "public", "stats": {"likes": 67, "quotes": 12, "reposts": 18, "replies": 25}, "likedBy": ["u2"], "repostedBy": ["u2"], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "p5", "authorId": "u5", "text": "Found the BEST vada pav in Mumbai! 🌮 Location in thread 👇", "media": "https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=800", "audience": "public", "stats": {"likes": 234, "quotes": 4, "reposts": 45, "replies": 38}, "likedBy": ["u1", "u3", "u4"], "repostedBy": ["u3"], "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.posts.insert_many(posts)
    
    # Seed reels
    reels = [
        {"id": "r1", "authorId": "u1", "videoUrl": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", "thumb": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=400", "caption": "Morning vibe check ☀️ #MumbaiLife", "stats": {"views": 2341, "likes": 456, "comments": 34}, "likedBy": ["u2", "u3"], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "r2", "authorId": "u3", "videoUrl": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4", "thumb": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400", "caption": "New digital art process 🎨✨", "stats": {"views": 5678, "likes": 892, "comments": 67}, "likedBy": ["u1", "u2", "u4"], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "r3", "authorId": "u5", "videoUrl": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4", "thumb": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=400", "caption": "Street food tour part 3! 🔥", "stats": {"views": 8934, "likes": 1234, "comments": 89}, "likedBy": ["u1", "u2", "u3", "u4"], "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.reels.insert_many(reels)
    
    # Seed tribes
    tribes = [
        {"id": "t1", "name": "Tech Builders India", "tags": ["tech", "startups", "coding"], "type": "public", "description": "A community for builders, makers, and tech enthusiasts across India.", "avatar": "https://api.dicebear.com/7.x/shapes/svg?seed=tech", "ownerId": "u2", "members": ["u2", "u1", "u4"], "memberCount": 3, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "t2", "name": "Digital Artists Hub", "tags": ["art", "design", "nft"], "type": "public", "description": "Share your art, get feedback, collaborate on projects.", "avatar": "https://api.dicebear.com/7.x/shapes/svg?seed=art", "ownerId": "u3", "members": ["u3", "u1"], "memberCount": 2, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "t3", "name": "Web3 India", "tags": ["crypto", "blockchain", "web3"], "type": "public", "description": "India's premier Web3 community. Learn, build, and grow together.", "avatar": "https://api.dicebear.com/7.x/shapes/svg?seed=web3", "ownerId": "u4", "members": ["u4", "u2"], "memberCount": 2, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "t4", "name": "Mumbai Foodies", "tags": ["food", "mumbai", "restaurants"], "type": "public", "description": "Best food spots in Mumbai. Reviews, recommendations, and more!", "avatar": "https://api.dicebear.com/7.x/shapes/svg?seed=food", "ownerId": "u5", "members": ["u5", "u1", "u3"], "memberCount": 3, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "t5", "name": "Free Speech Forum", "tags": ["debate", "politics", "society"], "type": "public", "description": "Open discussions on current affairs, politics, and society.", "avatar": "https://api.dicebear.com/7.x/shapes/svg?seed=forum", "ownerId": "u1", "members": ["u1", "u2", "u4"], "memberCount": 3, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.tribes.insert_many(tribes)
    
    # Seed wallet transactions
    wallet_transactions = [
        {"id": "wt1", "userId": "u1", "type": "topup", "amount": 500.0, "status": "completed", "description": "Initial wallet top-up", "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "wt2", "userId": "u2", "type": "topup", "amount": 1000.0, "status": "completed", "description": "Wallet top-up", "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "wt3", "userId": "u3", "type": "topup", "amount": 750.0, "status": "completed", "description": "Artist fund top-up", "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "wt4", "userId": "u4", "type": "topup", "amount": 2500.0, "status": "completed", "description": "Crypto earnings deposit", "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "wt5", "userId": "u5", "type": "topup", "amount": 300.0, "status": "completed", "description": "Food review earnings", "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "wt6", "userId": "demo_user", "type": "topup", "amount": 1500.0, "status": "completed", "description": "Demo account funding", "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.wallet_transactions.insert_many(wallet_transactions)
    
    # Seed venues
    venues = [
        {"id": "v1", "name": "Café Mondegar", "description": "Iconic café in Colaba with vintage vibes and live music", "avatar": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400", "location": "Colaba, Mumbai", "rating": 4.5, "menuItems": [{"id": "m1", "name": "Cappuccino", "price": 150}, {"id": "m2", "name": "Chicken Sandwich", "price": 250}, {"id": "m3", "name": "Chocolate Cake", "price": 180}], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "v2", "name": "The Bombay Canteen", "description": "Modern Indian cuisine with a contemporary twist", "avatar": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400", "location": "Lower Parel, Mumbai", "rating": 4.8, "menuItems": [{"id": "m4", "name": "Butter Chicken", "price": 450}, {"id": "m5", "name": "Biryani", "price": 380}, {"id": "m6", "name": "Masala Dosa", "price": 220}], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "v3", "name": "Starbucks Reserve", "description": "Premium coffee experience with artisanal brews", "avatar": "https://images.unsplash.com/photo-1511920170033-f8396924c348?w=400", "location": "BKC, Mumbai", "rating": 4.6, "menuItems": [{"id": "m7", "name": "Cold Brew", "price": 320}, {"id": "m8", "name": "Nitro Cold Brew", "price": 380}], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "v4", "name": "Soho House Mumbai", "description": "Members club with rooftop bar and restaurant", "avatar": "https://images.unsplash.com/photo-1514933651103-005eec06c04b?w=400", "location": "Juhu, Mumbai", "rating": 4.9, "menuItems": [{"id": "m9", "name": "Craft Cocktails", "price": 650}, {"id": "m10", "name": "Tapas Platter", "price": 890}], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "v5", "name": "Theobroma", "description": "Patisserie & bakery with heavenly desserts", "avatar": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=400", "location": "Multiple Locations", "rating": 4.7, "menuItems": [{"id": "m11", "name": "Chocolate Brownie", "price": 140}, {"id": "m12", "name": "Red Velvet Pastry", "price": 160}], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "v6", "name": "Phoenix Marketcity", "description": "Premier shopping and entertainment destination", "avatar": "https://images.unsplash.com/photo-1519567241046-7f570eee3ce6?w=400", "location": "Kurla, Mumbai", "rating": 4.4, "menuItems": [], "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.venues.insert_many(venues)
    
    # Seed events
    events = [
        {"id": "e1", "name": "TechCrunch Disrupt Mumbai", "description": "India's biggest tech conference featuring top founders, investors, and innovators", "image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800", "date": "2025-11-15", "location": "BKC, Mumbai", "tiers": [{"name": "General", "price": 5000}, {"name": "VIP", "price": 15000}], "vibeMeter": 92, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "e2", "name": "Mumbai Food Festival", "description": "Best street food from across India in one place", "image": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800", "date": "2025-11-22", "location": "Juhu Beach", "tiers": [{"name": "Entry", "price": 500}], "vibeMeter": 88, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "e3", "name": "Sunburn Festival 2025", "description": "Asia's biggest EDM festival with international DJs", "image": "https://images.unsplash.com/photo-1470229722913-7c0e2dbbafd3?w=800", "date": "2025-12-28", "location": "Goa", "tiers": [{"name": "GA", "price": 3500}, {"name": "VIP", "price": 8500}], "vibeMeter": 95, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "e4", "name": "Art Mumbai 2025", "description": "Contemporary art fair showcasing Indian and international artists", "image": "https://images.unsplash.com/photo-1531058020387-3be344556be6?w=800", "date": "2025-11-08", "location": "NCPA, Mumbai", "tiers": [{"name": "Standard", "price": 800}], "vibeMeter": 85, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "e5", "name": "Web3 India Summit", "description": "Leading blockchain and crypto conference", "image": "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800", "date": "2025-12-10", "location": "Bangalore", "tiers": [{"name": "Early Bird", "price": 2500}, {"name": "Regular", "price": 4000}], "vibeMeter": 90, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.events.insert_many(events)
    
    # Seed creators
    creators = [
        {"id": "c1", "userId": "u3", "displayName": "Ananya Reddy", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=ananya", "bio": "Digital art courses & NFT masterclasses", "items": [{"id": "i1", "name": "Digital Art Basics", "type": "course", "price": 2999}], "followers": 12400, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "c2", "userId": "u2", "displayName": "Raj Malhotra", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=raj", "bio": "Full-stack development bootcamp", "items": [{"id": "i2", "name": "React Masterclass", "type": "course", "price": 3999}], "followers": 8900, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.creators.insert_many(creators)
    
    # Seed messages
    messages = [
        {"id": "msg1", "fromId": "u1", "toId": "demo_user", "text": "Hey! Loved your recent post!", "read": False, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "msg2", "fromId": "demo_user", "toId": "u1", "text": "Thanks! How have you been?", "read": True, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.messages.insert_many(messages)
    
    # Seed notifications  
    notifications = [
        {"id": "n1", "userId": "demo_user", "type": "post_like", "payload": {"fromName": "Priya Sharma", "postId": "p1"}, "read": False, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "n2", "userId": "demo_user", "type": "tribe_join", "payload": {"fromName": "Raj Malhotra", "tribeId": "t1"}, "read": False, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.notifications.insert_many(notifications)
    
    return {"message": "Data seeded successfully", "users": len(users), "posts": len(posts), "reels": len(reels), "tribes": len(tribes), "wallet_transactions": len(wallet_transactions), "venues": len(venues), "events": len(events), "creators": len(creators), "messages": len(messages), "notifications": len(notifications)}

# ===== FILE UPLOAD ROUTES =====

@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload image or video file"""
    # Validate file type
    allowed_types = {
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
        'video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/webm'
    }
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="File type not supported")
    
    # Generate unique filename
    file_ext = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return URL path
    file_url = f"/uploads/{unique_filename}"
    
    return {
        "url": file_url,
        "filename": unique_filename,
        "content_type": file.content_type
    }

# ===== MESSAGE ROUTES =====

@api_router.get("/messages")
async def get_messages(userId: str):
    messages = await db.messages.find({
        "$or": [{"fromId": userId}, {"toId": userId}]
    }, {"_id": 0}).sort("createdAt", -1).to_list(100)
    
    # Enrich with peer data
    for message in messages:
        if message["fromId"] != userId:
            peer = await db.users.find_one({"id": message["fromId"]}, {"_id": 0})
            message["peer"] = peer
        else:
            peer = await db.users.find_one({"id": message["toId"]}, {"_id": 0})
            message["peer"] = peer
    
    return messages

@api_router.post("/messages")
async def send_message(message: MessageCreate, fromId: str, toId: str):
    message_obj = Message(fromId=fromId, toId=toId, **message.model_dump())
    doc = message_obj.model_dump()
    await db.messages.insert_one(doc)
    doc.pop('_id', None)
    
    # Enrich with user data
    from_user = await db.users.find_one({"id": fromId}, {"_id": 0})
    to_user = await db.users.find_one({"id": toId}, {"_id": 0})
    doc["fromUser"] = from_user
    doc["toUser"] = to_user
    
    return doc

@api_router.get("/messages/thread")
async def get_thread_messages(userId: str, peerId: str):
    messages = await db.messages.find({
        "$or": [
            {"fromId": userId, "toId": peerId},
            {"fromId": peerId, "toId": userId}
        ]
    }, {"_id": 0}).sort("createdAt", 1).to_list(1000)
    return messages

# ===== NOTIFICATION ROUTES =====

@api_router.get("/notifications")
async def get_notifications(userId: str):
    notifications = await db.notifications.find({"userId": userId}, {"_id": 0}).sort("createdAt", -1).to_list(100)
    return notifications

@api_router.post("/notifications/{notificationId}/read")
async def mark_notification_read(notificationId: str):
    await db.notifications.update_one({"id": notificationId}, {"$set": {"read": True}})
    return {"success": True}

# ===== VENUE ROUTES =====

@api_router.get("/venues")
async def get_venues(limit: int = 50):
    venues = await db.venues.find({}, {"_id": 0}).sort("rating", -1).to_list(limit)
    return venues

@api_router.get("/venues/{venueId}")
async def get_venue(venueId: str):
    venue = await db.venues.find_one({"id": venueId}, {"_id": 0})
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue

# ===== ORDER ROUTES =====

@api_router.post("/orders")
async def create_order(order: OrderCreate, userId: str):
    order_obj = Order(userId=userId, **order.model_dump())
    
    # Create Razorpay Payment Link
    try:
        payment_link_data = {
            "amount": int(order.total * 100),  # Amount in paise
            "currency": "INR",
            "accept_partial": False,
            "description": f"Order at venue {order.venueId}",
            "customer": {
                "name": "Customer",
                "email": "customer@example.com"
            },
            "notify": {
                "sms": False,
                "email": False
            },
            "reminder_enable": False,
            "callback_url": f"{os.environ.get('FRONTEND_URL', 'http://localhost:3000')}/order-success",
            "callback_method": "get"
        }
        
        # Only create payment link if Razorpay is properly configured
        if razorpay_key != 'rzp_test_xxx':
            payment_link = razorpay_client.payment_link.create(payment_link_data)
            order_obj.paymentLink = payment_link['short_url']
            order_obj.razorpayOrderId = payment_link['id']
        else:
            # Mock payment link for demo
            order_obj.paymentLink = f"https://razorpay.com/payment-links/demo_{order_obj.id}"
    except Exception as e:
        logging.error(f"Razorpay error: {e}")
        # Fallback to mock payment link
        order_obj.paymentLink = f"https://razorpay.com/payment-links/demo_{order_obj.id}"
    
    doc = order_obj.model_dump()
    await db.orders.insert_one(doc)
    doc.pop('_id', None)
    
    # Create notification
    notif = Notification(
        userId=userId,
        type="order_placed",
        payload={"orderId": order_obj.id, "total": order.total, "venueId": order.venueId}
    )
    await db.notifications.insert_one(notif.model_dump())
    
    return doc

@api_router.get("/orders")
async def get_user_orders(userId: str):
    orders = await db.orders.find({"userId": userId}, {"_id": 0}).sort("createdAt", -1).to_list(100)
    
    # Enrich with venue data
    for order in orders:
        venue = await db.venues.find_one({"id": order.get("venueId")}, {"_id": 0})
        order["venue"] = venue
    
    return orders

@api_router.patch("/orders/{orderId}/status")
async def update_order_status(orderId: str, status: str):
    await db.orders.update_one({"id": orderId}, {"$set": {"status": status}})
    
    # Notify user
    order = await db.orders.find_one({"id": orderId}, {"_id": 0})
    if order and status == "ready":
        notif = Notification(
            userId=order["userId"],
            type="order_ready",
            payload={"orderId": orderId}
        )
        await db.notifications.insert_one(notif.model_dump())
    
    return {"success": True, "status": status}

# ===== EVENT ROUTES =====

@api_router.get("/events")
async def get_events(limit: int = 50):
    events = await db.events.find({}, {"_id": 0}).sort("date", 1).to_list(limit)
    return events

@api_router.get("/events/{eventId}")
async def get_event(eventId: str):
    event = await db.events.find_one({"id": eventId}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@api_router.post("/events/{eventId}/book")
async def book_event_ticket(eventId: str, userId: str, tier: str = "General", quantity: int = 1):
    """Book event tickets using wallet balance"""
    # Get event
    event = await db.events.find_one({"id": eventId}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Get user
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Find tier price
    tiers = event.get("tiers", [])
    tier_data = next((t for t in tiers if t.get("name") == tier), None)
    if not tier_data:
        raise HTTPException(status_code=400, detail="Invalid tier")
    
    price_per_ticket = tier_data.get("price", 0)
    total_amount = price_per_ticket * quantity
    
    # Check balance
    current_balance = user.get("walletBalance", 0.0)
    if current_balance < total_amount:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")
    
    # Deduct from wallet
    new_balance = current_balance - total_amount
    await db.users.update_one({"id": userId}, {"$set": {"walletBalance": new_balance}})
    
    # Create tickets
    tickets = []
    for i in range(quantity):
        ticket = EventTicket(
            eventId=eventId,
            userId=userId,
            tier=tier,
            qrCode=str(uuid.uuid4()),
            status="active"
        )
        ticket_dict = ticket.model_dump()
        ticket_dict["eventName"] = event.get("name", "Event")
        ticket_dict["eventDate"] = event.get("date", "")
        ticket_dict["eventLocation"] = event.get("location", "")
        ticket_dict["eventImage"] = event.get("image", "")
        ticket_dict["price"] = price_per_ticket
        await db.event_tickets.insert_one(ticket_dict)
        tickets.append(ticket_dict)
    
    # Record transaction
    transaction = WalletTransaction(
        userId=userId,
        type="payment",
        amount=total_amount,
        description=f"Ticket purchase: {event.get('name', 'Event')} ({quantity}x {tier})",
        metadata={"eventId": eventId, "tier": tier, "quantity": quantity}
    )
    await db.wallet_transactions.insert_one(transaction.model_dump())
    
    # Award Loop Credits (bonus for ticket purchase)
    credits_earned = 20 * quantity  # 20 credits per ticket
    if credits_earned > 0:
        credit_entry = LoopCredit(
            userId=userId,
            amount=credits_earned,
            type="earn",
            source="event",
            description=f"Bonus for buying {quantity} ticket(s)"
        )
        await db.loop_credits.insert_one(credit_entry.model_dump())
    
    return {
        "success": True,
        "tickets": tickets,
        "balance": new_balance,
        "creditsEarned": credits_earned,
        "message": f"Successfully booked {quantity} ticket(s)!"
    }

@api_router.get("/tickets/{userId}")
async def get_user_tickets(userId: str):
    """Get all tickets for a user"""
    tickets = await db.event_tickets.find({"userId": userId}, {"_id": 0}).sort("purchasedAt", -1).to_list(100)
    return tickets

@api_router.get("/tickets/{userId}/{ticketId}")
async def get_ticket_details(userId: str, ticketId: str):
    """Get specific ticket details"""
    ticket = await db.event_tickets.find_one({"id": ticketId, "userId": userId}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

# ===== CREATOR ROUTES =====

@api_router.get("/creators")
async def get_creators(limit: int = 50):
    creators = await db.creators.find({}, {"_id": 0}).sort("followers", -1).to_list(limit)
    return creators

@api_router.get("/creators/{creatorId}")
async def get_creator(creatorId: str):
    creator = await db.creators.find_one({"id": creatorId}, {"_id": 0})
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")
    return creator

# ===== WALLET ROUTES =====

@api_router.get("/wallet")
async def get_wallet(userId: str):
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transactions = await db.wallet_transactions.find({"userId": userId}, {"_id": 0}).sort("createdAt", -1).to_list(100)
    
    return {
        "balance": user.get("walletBalance", 0.0),
        "kycTier": user.get("kycTier", 1),
        "transactions": transactions
    }

@api_router.post("/wallet/topup")
async def topup_wallet(request: TopUpRequest, userId: str):
    # Mock payment success
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_balance = user.get("walletBalance", 0.0) + request.amount
    await db.users.update_one({"id": userId}, {"$set": {"walletBalance": new_balance}})
    
    # Record transaction
    transaction = WalletTransaction(
        userId=userId,
        type="topup",
        amount=request.amount,
        description="Wallet top-up"
    )
    await db.wallet_transactions.insert_one(transaction.model_dump())
    
    return {"balance": new_balance, "success": True}

@api_router.post("/wallet/payment")
async def make_payment(request: PaymentRequest, userId: str):
    """Process payment at venue using wallet balance"""
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_balance = user.get("walletBalance", 0.0)
    
    # Check sufficient balance
    if current_balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    # Deduct amount
    new_balance = current_balance - request.amount
    await db.users.update_one({"id": userId}, {"$set": {"walletBalance": new_balance}})
    
    # Record transaction
    transaction = WalletTransaction(
        userId=userId,
        type="payment",
        amount=request.amount,
        description=request.description or f"Payment at {request.venueName or 'venue'}",
        metadata={"venueId": request.venueId, "venueName": request.venueName}
    )
    await db.wallet_transactions.insert_one(transaction.model_dump())
    
    # Award Loop Credits (2% cashback)
    credits_earned = int(request.amount * 0.02)
    if credits_earned > 0:
        credit_entry = {
            "id": str(uuid.uuid4()),
            "userId": userId,
            "amount": credits_earned,
            "type": "earn",
            "source": "payment_cashback",
            "description": f"2% cashback on ₹{request.amount} payment",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
        await db.loop_credits.insert_one(credit_entry)
    
    return {
        "success": True,
        "balance": new_balance,
        "creditsEarned": credits_earned,
        "transactionId": transaction.id
    }


# ===== LOOP CREDITS ROUTES =====

@api_router.get("/credits/{userId}")
async def get_user_credits(userId: str):
    """Get user's Loop Credits balance and history"""
    # Get total credits
    credits = await db.loop_credits.find({"userId": userId}, {"_id": 0}).to_list(1000)
    
    earned = sum(c["amount"] for c in credits if c["type"] == "earn")
    spent = sum(c["amount"] for c in credits if c["type"] == "spend")
    balance = earned - spent
    
    # Get analytics
    analytics = await db.user_analytics.find_one({"userId": userId}, {"_id": 0})
    if not analytics:
        analytics = UserAnalytics(userId=userId, totalCredits=balance).model_dump()
        await db.user_analytics.insert_one(analytics)
    
    return {
        "balance": balance,
        "earned": earned,
        "spent": spent,
        "history": credits[:20],  # Last 20 transactions
        "tier": analytics.get("tier", "Bronze"),
        "vibeRank": analytics.get("vibeRank", 0)
    }

@api_router.post("/credits/earn")
async def earn_credits(userId: str, amount: int, source: str, description: str = ""):
    """Award Loop Credits to user"""
    credit = LoopCredit(
        userId=userId,
        amount=amount,
        type="earn",
        source=source,
        description=description
    )
    await db.loop_credits.insert_one(credit.model_dump())
    
    # Update analytics
    await db.user_analytics.update_one(
        {"userId": userId},
        {"$inc": {"totalCredits": amount}, "$set": {"lastUpdated": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    
    return {"success": True, "amount": amount, "balance": await get_credits_balance(userId)}

@api_router.post("/credits/spend")
async def spend_credits(userId: str, amount: int, source: str, description: str = ""):
    """Deduct Loop Credits from user"""
    balance = await get_credits_balance(userId)
    if balance < amount:
        raise HTTPException(status_code=400, detail="Insufficient credits")
    
    credit = LoopCredit(
        userId=userId,
        amount=amount,
        type="spend",
        source=source,
        description=description
    )
    await db.loop_credits.insert_one(credit.model_dump())
    
    # Update analytics
    await db.user_analytics.update_one(
        {"userId": userId},
        {"$inc": {"totalCredits": -amount}, "$set": {"lastUpdated": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    
    return {"success": True, "amount": amount, "balance": await get_credits_balance(userId)}

async def get_credits_balance(userId: str) -> int:
    """Helper to get current credits balance"""
    credits = await db.loop_credits.find({"userId": userId}, {"_id": 0}).to_list(1000)
    earned = sum(c["amount"] for c in credits if c["type"] == "earn")
    spent = sum(c["amount"] for c in credits if c["type"] == "spend")
    return earned - spent

# ===== CHECK-IN ROUTES =====

@api_router.post("/checkins")
async def create_checkin(userId: str, venueId: str):
    """Check-in to a venue"""
    # Check if already checked in
    existing = await db.checkins.find_one({"userId": userId, "status": "active"}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in to a venue")
    
    checkin = CheckIn(userId=userId, venueId=venueId)
    await db.checkins.insert_one(checkin.model_dump())
    
    # Award credits for check-in
    await earn_credits(userId, 10, "checkin", f"Check-in at venue {venueId}")
    
    # Update analytics
    await db.user_analytics.update_one(
        {"userId": userId},
        {"$inc": {"totalCheckins": 1}, "$set": {"lastUpdated": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    
    # Update venue vibe meter
    await update_venue_vibe_meter(venueId)
    
    return {"success": True, "checkin": checkin.model_dump(), "creditsEarned": 10}

@api_router.post("/checkins/{checkinId}/checkout")
async def checkout(checkinId: str):
    """Check-out from a venue"""
    checkin = await db.checkins.find_one({"id": checkinId}, {"_id": 0})
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in not found")
    
    await db.checkins.update_one(
        {"id": checkinId},
        {"$set": {"checkedOutAt": datetime.now(timezone.utc).isoformat(), "status": "completed"}}
    )
    
    # Update venue vibe meter
    await update_venue_vibe_meter(checkin["venueId"])
    
    return {"success": True}

@api_router.get("/checkins/venue/{venueId}")
async def get_venue_checkins(venueId: str):
    """Get active check-ins at a venue"""
    checkins = await db.checkins.find({"venueId": venueId, "status": "active"}, {"_id": 0}).to_list(100)
    
    # Enrich with user data
    for checkin in checkins:
        user = await db.users.find_one({"id": checkin["userId"]}, {"_id": 0})
        if user:
            checkin["user"] = {"id": user["id"], "name": user["name"], "avatar": user["avatar"]}
    
    return {"count": len(checkins), "checkins": checkins}

@api_router.get("/checkins/user/{userId}/active")
async def get_user_active_checkin(userId: str):
    """Get user's active check-in"""
    checkin = await db.checkins.find_one({"userId": userId, "status": "active"}, {"_id": 0})
    if not checkin:
        return {"checkedIn": False}
    
    # Get venue details
    venue = await db.venues.find_one({"id": checkin["venueId"]}, {"_id": 0})
    
    return {"checkedIn": True, "checkin": checkin, "venue": venue}

async def update_venue_vibe_meter(venueId: str):
    """Update venue's vibe meter based on active check-ins"""
    checkins = await db.checkins.find({"venueId": venueId, "status": "active"}, {"_id": 0}).to_list(100)
    count = len(checkins)
    
    # Calculate vibe meter (0-100 scale)
    vibe_meter = min(100, count * 10)  # 10 points per active user
    
    await db.venues.update_one(
        {"id": venueId},
        {"$set": {"vibeMeter": vibe_meter}}
    )
    
    return vibe_meter

# ===== OFFERS ROUTES =====

@api_router.get("/offers/venue/{venueId}")
async def get_venue_offers(venueId: str):
    """Get active offers for a venue"""
    now = datetime.now(timezone.utc).isoformat()
    offers = await db.offers.find(
        {"venueId": venueId, "validUntil": {"$gt": now}},
        {"_id": 0}
    ).to_list(100)
    
    return offers

@api_router.post("/offers/{offerId}/claim")
async def claim_offer(offerId: str, userId: str):
    """Claim an offer"""
    offer = await db.offers.find_one({"id": offerId}, {"_id": 0})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")
    
    # Check if already claimed
    existing_claim = await db.offer_claims.find_one({"userId": userId, "offerId": offerId, "status": "active"}, {"_id": 0})
    if existing_claim:
        raise HTTPException(status_code=400, detail="Offer already claimed")
    
    # Check claim limit
    if offer["claimedCount"] >= offer["claimLimit"]:
        raise HTTPException(status_code=400, detail="Offer claim limit reached")
    
    # Check credits
    if offer["creditsRequired"] > 0:
        balance = await get_credits_balance(userId)
        if balance < offer["creditsRequired"]:
            raise HTTPException(status_code=400, detail="Insufficient credits")
        
        # Deduct credits
        await spend_credits(userId, offer["creditsRequired"], "offer", f"Claimed offer: {offer['title']}")
    
    # Create claim
    claim = OfferClaim(
        userId=userId,
        offerId=offerId,
        venueId=offer["venueId"]
    )
    await db.offer_claims.insert_one(claim.model_dump())
    
    # Update offer claimed count
    await db.offers.update_one({"id": offerId}, {"$inc": {"claimedCount": 1}})
    
    return {"success": True, "claim": claim.model_dump()}

@api_router.get("/offers/claims/{userId}")
async def get_user_claims(userId: str):
    """Get user's claimed offers"""
    claims = await db.offer_claims.find({"userId": userId, "status": "active"}, {"_id": 0}).to_list(100)
    
    # Enrich with offer and venue details
    for claim in claims:
        offer = await db.offers.find_one({"id": claim["offerId"]}, {"_id": 0})
        venue = await db.venues.find_one({"id": claim["venueId"]}, {"_id": 0})
        if offer:
            claim["offer"] = offer
        if venue:
            claim["venue"] = venue
    
    return claims

# ===== POLLS ROUTES =====

@api_router.post("/polls")
async def create_poll(postId: str, question: str, options: List[str], endsAt: str):
    """Create a poll for a post"""
    poll_options = [{"id": str(i), "text": opt, "votes": 0} for i, opt in enumerate(options)]
    
    poll = Poll(
        postId=postId,
        question=question,
        options=poll_options,
        endsAt=endsAt
    )
    await db.polls.insert_one(poll.model_dump())
    
    return poll.model_dump()

@api_router.post("/polls/{pollId}/vote")
async def vote_on_poll(pollId: str, userId: str, optionId: str):
    """Vote on a poll"""
    poll = await db.polls.find_one({"id": pollId}, {"_id": 0})
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    
    # Check if already voted
    if userId in poll["votedBy"]:
        raise HTTPException(status_code=400, detail="Already voted")
    
    # Update poll
    for option in poll["options"]:
        if option["id"] == optionId:
            option["votes"] += 1
            break
    
    poll["totalVotes"] += 1
    poll["votedBy"].append(userId)
    
    await db.polls.update_one(
        {"id": pollId},
        {"$set": {"options": poll["options"], "totalVotes": poll["totalVotes"], "votedBy": poll["votedBy"]}}
    )
    
    # Award credits for voting
    await earn_credits(userId, 2, "poll_vote", f"Voted on poll {pollId}")
    
    return {"success": True, "poll": poll}

@api_router.get("/polls/{pollId}")
async def get_poll(pollId: str):
    """Get poll details"""
    poll = await db.polls.find_one({"id": pollId}, {"_id": 0})
    if not poll:
        raise HTTPException(status_code=404, detail="Poll not found")
    return poll

# ===== BOOKMARKS ROUTES =====

@api_router.post("/bookmarks")
async def create_bookmark(userId: str, postId: str):
    """Bookmark a post"""
    existing = await db.bookmarks.find_one({"userId": userId, "postId": postId}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Post already bookmarked")
    
    bookmark = Bookmark(userId=userId, postId=postId)
    await db.bookmarks.insert_one(bookmark.model_dump())
    
    return {"success": True, "bookmark": bookmark.model_dump()}

@api_router.delete("/bookmarks")
async def remove_bookmark(userId: str, postId: str):
    """Remove bookmark"""
    result = await db.bookmarks.delete_one({"userId": userId, "postId": postId})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    return {"success": True}

@api_router.get("/bookmarks/{userId}")
async def get_user_bookmarks(userId: str):
    """Get user's bookmarks"""
    bookmarks = await db.bookmarks.find({"userId": userId}, {"_id": 0}).sort("createdAt", -1).to_list(100)
    
    # Enrich with post details
    posts = []
    for bookmark in bookmarks:
        post = await db.posts.find_one({"id": bookmark["postId"]}, {"_id": 0})
        if post:
            # Get author details
            author = await db.users.find_one({"id": post["authorId"]}, {"_id": 0})
            if author:
                post["author"] = author
            posts.append(post)
    
    return posts

# ===== TRIBE CHALLENGES ROUTES =====

@api_router.get("/tribes/{tribeId}/challenges")
async def get_tribe_challenges(tribeId: str):
    """Get active challenges for a tribe"""
    now = datetime.now(timezone.utc).isoformat()
    challenges = await db.tribe_challenges.find(
        {"tribeId": tribeId, "endDate": {"$gt": now}},
        {"_id": 0}
    ).to_list(100)
    
    return challenges

@api_router.post("/challenges/{challengeId}/join")
async def join_challenge(challengeId: str, userId: str):
    """Join a tribe challenge"""
    challenge = await db.tribe_challenges.find_one({"id": challengeId}, {"_id": 0})
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if userId in challenge["participants"]:
        raise HTTPException(status_code=400, detail="Already joined this challenge")
    
    await db.tribe_challenges.update_one(
        {"id": challengeId},
        {"$push": {"participants": userId}}
    )
    
    return {"success": True}

@api_router.post("/challenges/{challengeId}/complete")
async def complete_challenge(challengeId: str, userId: str):
    """Mark challenge as completed"""
    challenge = await db.tribe_challenges.find_one({"id": challengeId}, {"_id": 0})
    if not challenge:
        raise HTTPException(status_code=404, detail="Challenge not found")
    
    if userId not in challenge["participants"]:
        raise HTTPException(status_code=400, detail="Not a participant")
    
    if userId in challenge["completedBy"]:
        raise HTTPException(status_code=400, detail="Challenge already completed")
    
    # Mark as completed
    await db.tribe_challenges.update_one(
        {"id": challengeId},
        {"$push": {"completedBy": userId}}
    )
    
    # Award credits
    await earn_credits(userId, challenge["reward"], "challenge", f"Completed challenge: {challenge['title']}")
    
    # Update analytics
    await db.user_analytics.update_one(
        {"userId": userId},
        {"$inc": {"totalChallengesCompleted": 1}, "$set": {"lastUpdated": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )
    
    return {"success": True, "reward": challenge["reward"]}

# ===== EVENT TICKETS ROUTES =====

@api_router.post("/events/{eventId}/tickets")
async def claim_event_ticket(eventId: str, userId: str, tier: str = "General"):
    """Claim a free event ticket"""
    event = await db.events.find_one({"id": eventId}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if already has ticket
    existing = await db.event_tickets.find_one({"eventId": eventId, "userId": userId, "status": "active"}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Already have a ticket for this event")
    
    # Create ticket
    ticket = EventTicket(
        eventId=eventId,
        userId=userId,
        tier=tier
    )
    await db.event_tickets.insert_one(ticket.model_dump())
    
    return {"success": True, "ticket": ticket.model_dump()}

@api_router.get("/tickets/{userId}")
async def get_user_tickets(userId: str):
    """Get user's event tickets"""
    tickets = await db.event_tickets.find({"userId": userId, "status": "active"}, {"_id": 0}).to_list(100)
    
    # Enrich with event details
    for ticket in tickets:
        event = await db.events.find_one({"id": ticket["eventId"]}, {"_id": 0})
        if event:
            ticket["event"] = event
    
    return tickets

@api_router.post("/tickets/{ticketId}/use")
async def use_ticket(ticketId: str, qrCode: str):
    """Mark ticket as used (scanned at venue)"""
    ticket = await db.event_tickets.find_one({"id": ticketId, "qrCode": qrCode}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found or invalid QR code")
    
    if ticket["status"] != "active":
        raise HTTPException(status_code=400, detail="Ticket already used or cancelled")
    
    await db.event_tickets.update_one(
        {"id": ticketId},
        {"$set": {"status": "used", "usedAt": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Award credits for attending
    await earn_credits(ticket["userId"], 50, "event_attendance", f"Attended event")
    
    return {"success": True, "message": "Ticket validated"}

# ===== USER INTERESTS & ONBOARDING =====

@api_router.post("/users/{userId}/interests")
async def update_user_interests(userId: str, interests: str, language: str = "en"):
    """Update user interests and language preference"""
    # Parse comma-separated interests
    interest_list = [i.strip() for i in interests.split(',') if i.strip()]
    
    user_interest = UserInterest(
        userId=userId,
        interests=interest_list,
        language=language,
        onboardingComplete=True
    )
    
    await db.user_interests.update_one(
        {"userId": userId},
        {"$set": user_interest.model_dump()},
        upsert=True
    )
    
    return {"success": True}

@api_router.get("/users/{userId}/interests")
async def get_user_interests(userId: str):
    """Get user interests"""
    interests = await db.user_interests.find_one({"userId": userId}, {"_id": 0})
    if not interests:
        return {"interests": [], "language": "en", "onboardingComplete": False}
    return interests

# ===== CONSENT ROUTES =====

@api_router.post("/users/{userId}/consents")
async def save_user_consents(userId: str, consent_data: UserConsent):
    """Save user consent preferences (DPDP compliance)"""
    consent_dict = consent_data.model_dump()
    consent_dict["updatedAt"] = datetime.now(timezone.utc).isoformat()
    
    # Mask Aadhaar number for storage (store only last 4 digits for display)
    if consent_dict.get("aadhaarNumber"):
        # In production, this should be encrypted
        consent_dict["aadhaarNumberMasked"] = f"XXXX-XXXX-{consent_dict['aadhaarNumber'][-4:]}"
    
    await db.user_consents.update_one(
        {"userId": userId},
        {"$set": consent_dict},
        upsert=True
    )
    
    return {"success": True, "message": "Consent preferences saved"}

# ===== AI ROUTES =====
class RankRequest(BaseModel):
    query: str
    documents: List[str]

class RankResponse(BaseModel):
    items: List[dict]

class SafetyRequest(BaseModel):
    text: str

class TranslateRequest(BaseModel):
    text: str
    target_language: str
    source_language: Optional[str] = None

class InsightRequest(BaseModel):
    text: str
    task: str = Field(default="summarize")  # summarize, sentiment

@api_router.post("/ai/rank")
async def ai_rank(req: RankRequest):
    # Mock implementation - ranks by keyword relevance
    scores = []
    query_lower = req.query.lower()
    
    for i, doc in enumerate(req.documents):
        doc_lower = doc.lower()
        # Simple scoring: count query word occurrences + exact matches
        score = doc_lower.count(query_lower)
        if query_lower in doc_lower:
            score += 2  # Bonus for containing the query
        scores.append({"index": i, "score": score, "document": doc})
    
    # Sort by score descending
    items = sorted(scores, key=lambda x: x["score"], reverse=True)
    return {"items": items}

@api_router.post("/ai/safety")
async def ai_safety(req: SafetyRequest):
    # Mock implementation for testing - returns safe for most content
    text_lower = req.text.lower()
    unsafe_keywords = ["hate", "violence", "kill", "bomb", "terrorist"]
    
    if any(keyword in text_lower for keyword in unsafe_keywords):
        return {"safe": False, "categories": ["violence", "hate"]}
    else:
        return {"safe": True, "categories": []}

@api_router.post("/ai/translate")
async def ai_translate(req: TranslateRequest):
    # Mock implementation for testing
    translations = {
        "hello": {"hi": "नमस्ते", "es": "hola", "fr": "bonjour"},
        "goodbye": {"hi": "अलविदा", "es": "adiós", "fr": "au revoir"},
        "thank you": {"hi": "धन्यवाद", "es": "gracias", "fr": "merci"}
    }
    
    text_lower = req.text.lower()
    target = req.target_language.lower()
    
    if text_lower in translations and target in translations[text_lower]:
        return {"translated_text": translations[text_lower][target]}
    else:
        return {"translated_text": f"[Mock translation of '{req.text}' to {req.target_language}]"}

@api_router.post("/ai/insight")
async def ai_insight(req: InsightRequest):
    # Mock implementation for testing
    text_length = len(req.text)
    word_count = len(req.text.split())
    
    if req.task == "summarize":
        result = f"• Text contains {word_count} words and {text_length} characters\n• Content appears to be informational in nature\n• Summary generated using mock AI service"
    elif req.task == "sentiment":
        # Simple sentiment analysis
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "happy"]
        negative_words = ["bad", "terrible", "awful", "sad", "angry", "hate"]
        
        text_lower = req.text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = "positive"
            score = 0.7
        elif neg_count > pos_count:
            sentiment = "negative" 
            score = 0.3
        else:
            sentiment = "neutral"
            score = 0.5
            
        result = f'{{"sentiment": "{sentiment}", "score": {score}}}'
    else:
        result = f"Key insights: This text has {word_count} words. It appears to be written in a conversational tone. Mock analysis suggests the content is informational."
    
    return {"result": result}

@api_router.get("/users/{userId}/consents")
async def get_user_consents(userId: str):
    """Get user consent preferences"""
    consents = await db.user_consents.find_one({"userId": userId}, {"_id": 0})
    if not consents:
        return UserConsent(userId=userId).model_dump()
    return consents

# ===== ANALYTICS ROUTES =====

@api_router.get("/analytics/{userId}")
async def get_user_analytics(userId: str):
    """Get comprehensive user analytics dashboard"""
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all user posts
    posts = await db.posts.find({"authorId": userId}, {"_id": 0}).to_list(None)
    reels = await db.reels.find({"authorId": userId}, {"_id": 0}).to_list(None)
    
    # Calculate engagement
    total_likes = sum(len(p.get("likes", [])) for p in posts) + sum(len(r.get("likes", [])) for r in reels)
    total_comments = sum(len(p.get("comments", [])) for p in posts) + sum(len(r.get("comments", [])) for r in reels)
    total_shares = sum(p.get("shares", 0) for p in posts) + sum(r.get("shares", 0) for r in reels)
    
    # Get follower count
    followers_count = len(user.get("followers", []))
    following_count = len(user.get("following", []))
    
    # Daily/Weekly engagement (last 7 days)
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)
    
    recent_posts = [p for p in posts if datetime.fromisoformat(p.get("createdAt", now.isoformat())) > week_ago]
    recent_reels = [r for r in reels if datetime.fromisoformat(r.get("createdAt", now.isoformat())) > week_ago]
    
    weekly_engagement = {
        "posts": len(recent_posts),
        "reels": len(recent_reels),
        "likes": sum(len(p.get("likes", [])) for p in recent_posts) + sum(len(r.get("likes", [])) for r in recent_reels),
        "comments": sum(len(p.get("comments", [])) for p in recent_posts) + sum(len(r.get("comments", [])) for r in recent_reels)
    }
    
    return {
        "userId": userId,
        "totalPosts": len(posts),
        "totalReels": len(reels),
        "totalLikes": total_likes,
        "totalComments": total_comments,
        "totalShares": total_shares,
        "followersCount": followers_count,
        "followingCount": following_count,
        "weeklyEngagement": weekly_engagement,
        "engagementRate": round((total_likes + total_comments) / max(len(posts) + len(reels), 1), 2),
        "tier": user.get("tier", "Bronze")
    }

@api_router.get("/analytics/creator/{userId}")
async def get_creator_dashboard(userId: str):
    """Get creator-specific analytics"""
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    posts = await db.posts.find({"authorId": userId}, {"_id": 0}).to_list(None)
    reels = await db.reels.find({"authorId": userId}, {"_id": 0}).to_list(None)
    
    # Calculate total reach (views)
    total_views = sum(p.get("views", 0) for p in posts) + sum(r.get("views", 0) for r in reels)
    
    # Follower growth (mock data - in production, track historical data)
    followers = user.get("followers", [])
    
    # Top performing content
    top_posts = sorted(posts, key=lambda x: len(x.get("likes", [])), reverse=True)[:5]
    top_reels = sorted(reels, key=lambda x: len(x.get("likes", [])), reverse=True)[:5]
    
    return {
        "userId": userId,
        "followersCount": len(followers),
        "followersGrowth": "+15%",  # Mock - track historical data
        "totalReach": total_views,
        "avgEngagementRate": "8.5%",  # Mock calculation
        "topPosts": top_posts,
        "topReels": top_reels,
        "contentBreakdown": {
            "posts": len(posts),
            "reels": len(reels),
            "totalEngagement": sum(len(p.get("likes", [])) for p in posts) + sum(len(r.get("likes", [])) for r in reels)
        }
    }

@api_router.get("/analytics/tribe/{tribeId}")
async def get_tribe_analytics(tribeId: str):
    """Get tribe-specific analytics"""
    tribe = await db.tribes.find_one({"id": tribeId}, {"_id": 0})
    if not tribe:
        raise HTTPException(status_code=404, detail="Tribe not found")
    
    members = tribe.get("members", [])
    
    # Get tribe posts
    tribe_posts = await db.posts.find({"authorId": {"$in": members}}, {"_id": 0}).to_list(None)
    
    # Most active members
    member_activity = {}
    for post in tribe_posts:
        author_id = post.get("authorId")
        member_activity[author_id] = member_activity.get(author_id, 0) + 1
    
    top_contributors = sorted(member_activity.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Popular posts
    popular_posts = sorted(tribe_posts, key=lambda x: len(x.get("likes", [])), reverse=True)[:10]
    
    return {
        "tribeId": tribeId,
        "tribeName": tribe.get("name"),
        "memberCount": len(members),
        "totalPosts": len(tribe_posts),
        "activeMembers": len(member_activity),
        "topContributors": [{"userId": uid, "postCount": count} for uid, count in top_contributors],
        "popularPosts": popular_posts,
        "engagementRate": round(sum(len(p.get("likes", [])) for p in tribe_posts) / max(len(tribe_posts), 1), 2)
    }

@api_router.get("/analytics/wallet/{userId}")
async def get_wallet_analytics(userId: str):
    """Get wallet-specific analytics"""
    wallet = await db.users.find_one({"id": userId}, {"_id": 0, "walletBalance": 1})
    if not wallet:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get transactions
    transactions = await db.wallet_transactions.find({"userId": userId}, {"_id": 0}).to_list(None)
    
    # Calculate spending
    total_spent = sum(t.get("amount", 0) for t in transactions if t.get("type") == "payment")
    total_added = sum(t.get("amount", 0) for t in transactions if t.get("type") == "topup")
    
    # Get credits earned
    credits = await db.loop_credits.find({"userId": userId}, {"_id": 0}).to_list(None)
    total_credits_earned = sum(c.get("amount", 0) for c in credits if c.get("type") == "earn")
    
    # Spending by category (mock)
    spending_breakdown = {
        "venues": 0,
        "events": 0,
        "marketplace": 0,
        "other": 0
    }
    
    for txn in transactions:
        if txn.get("type") == "payment":
            metadata = txn.get("metadata", {})
            venue_name = metadata.get("venueName", "")
            if "café" in venue_name.lower() or "restaurant" in venue_name.lower():
                spending_breakdown["venues"] += txn.get("amount", 0)
            elif "ticket" in venue_name.lower() or "event" in venue_name.lower():
                spending_breakdown["events"] += txn.get("amount", 0)
            else:
                spending_breakdown["other"] += txn.get("amount", 0)
    
    return {
        "userId": userId,
        "currentBalance": wallet.get("walletBalance", 0),
        "totalSpent": total_spent,
        "totalAdded": total_added,
        "totalCreditsEarned": total_credits_earned,
        "transactionCount": len(transactions),
        "spendingBreakdown": spending_breakdown,
        "avgTransactionAmount": round(total_spent / max(len([t for t in transactions if t.get("type") == "payment"]), 1), 2),
        "recentTransactions": sorted(transactions, key=lambda x: x.get("createdAt", ""), reverse=True)[:10]
    }

@api_router.get("/analytics/admin")
async def get_admin_dashboard(adminUserId: str):
    """Get platform-wide admin analytics"""
    # Verify admin (in production, check admin role)
    admin = await db.users.find_one({"id": adminUserId}, {"_id": 0})
    if not admin:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Count totals
    total_users = await db.users.count_documents({})
    total_posts = await db.posts.count_documents({})
    total_reels = await db.reels.count_documents({})
    total_tribes = await db.tribes.count_documents({})
    total_rooms = await db.vibe_rooms.count_documents({})
    
    # Active users (posted in last 7 days)
    from datetime import timedelta
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    active_users = await db.posts.distinct("authorId", {"createdAt": {"$gte": week_ago}})
    
    # Platform engagement
    all_posts = await db.posts.find({}, {"_id": 0, "likes": 1, "comments": 1}).to_list(None)
    total_likes = sum(len(p.get("likes", [])) for p in all_posts)
    total_comments = sum(len(p.get("comments", [])) for p in all_posts)
    
    return {
        "totalUsers": total_users,
        "activeUsers": len(active_users),
        "totalPosts": total_posts,
        "totalReels": total_reels,
        "totalTribes": total_tribes,
        "totalRooms": total_rooms,
        "totalLikes": total_likes,
        "totalComments": total_comments,
        "platformEngagementRate": round((total_likes + total_comments) / max(total_posts, 1), 2),
        "growthRate": "+23%",  # Mock - track historical data
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ===== USER SETTINGS ROUTES =====

@api_router.put("/users/{userId}/settings")
async def update_user_settings(userId: str, updates: dict):
    """Update user profile settings"""
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Allowed fields to update
    allowed_fields = ["name", "bio", "avatar", "location", "website", "interests"]
    update_data = {k: v for k, v in updates.items() if k in allowed_fields}
    
    if update_data:
        await db.users.update_one({"id": userId}, {"$set": update_data})
    
    updated_user = await db.users.find_one({"id": userId}, {"_id": 0})
    return updated_user

@api_router.get("/users/{userId}/content")
async def get_user_content(userId: str, category: str = "all"):
    """Get user's content categorized by type"""
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = {}
    
    if category in ["all", "posts"]:
        posts = await db.posts.find({"authorId": userId}, {"_id": 0}).sort("createdAt", -1).to_list(None)
        result["posts"] = posts
    
    if category in ["all", "reels"]:
        reels = await db.reels.find({"authorId": userId}, {"_id": 0}).sort("createdAt", -1).to_list(None)
        result["reels"] = reels
    
    if category in ["all", "products"]:
        products = await db.marketplace.find({"sellerId": userId}, {"_id": 0}).sort("createdAt", -1).to_list(None)
        result["products"] = products if products else []
    
    return result


# ===== FRIEND REQUEST ROUTES =====

@api_router.post("/friend-requests")
async def send_friend_request(fromUserId: str, toUserId: str):
    """Send a friend request"""
    # Validate: cannot send to yourself
    if fromUserId == toUserId:
        raise HTTPException(status_code=400, detail="Cannot send friend request to yourself")
    
    # Check if either user blocked the other
    if await is_blocked(fromUserId, toUserId) or await is_blocked(toUserId, fromUserId):
        raise HTTPException(status_code=403, detail="Cannot send friend request to this user")
    
    # Check if already friends
    if await are_friends(fromUserId, toUserId):
        raise HTTPException(status_code=400, detail="Already friends")
    
    # Check if request already exists
    existing_request = await db.friend_requests.find_one({
        "fromUserId": fromUserId,
        "toUserId": toUserId,
        "status": "pending"
    }, {"_id": 0})
    
    if existing_request:
        raise HTTPException(status_code=400, detail="Friend request already sent")
    
    # Create friend request
    friend_request = FriendRequest(fromUserId=fromUserId, toUserId=toUserId)
    await db.friend_requests.insert_one(friend_request.model_dump())
    
    # Get sender info
    from_user = await db.users.find_one({"id": fromUserId}, {"_id": 0})
    
    # If user not found in MongoDB, create a basic user object
    if not from_user:
        from_user = {
            "id": fromUserId,
            "name": "Demo User",
            "handle": "demo_user",
            "avatar": f"https://api.dicebear.com/7.x/avataaars/svg?seed={fromUserId}"
        }
    
    # Create notification
    notification = Notification(
        userId=toUserId,
        type="friend_request",
        content=f"{from_user.get('name', 'Someone')} sent you a friend request",
        link=f"/profile/{fromUserId}",
        payload={"fromUser": from_user}
    )
    await db.notifications.insert_one(notification.model_dump())
    
    # Real-time notification via WebSocket
    await emit_to_user(toUserId, 'friend_request', {
        'id': friend_request.id,
        'from_user': from_user,
        'status': 'pending',
        'createdAt': friend_request.createdAt
    })
    
    return {"success": True, "requestId": friend_request.id, "status": "pending"}

@api_router.get("/friend-requests")
async def get_friend_requests(userId: str):
    """Get all friend requests for a user (sent and received)"""
    # Get incoming requests (where user is recipient)
    incoming = await db.friend_requests.find({
        "toUserId": userId
    }, {"_id": 0}).to_list(100)
    
    # Get outgoing requests (where user is sender)
    outgoing = await db.friend_requests.find({
        "fromUserId": userId
    }, {"_id": 0}).to_list(100)
    
    # Enrich with user data
    for req in incoming:
        from_user = await db.users.find_one({"id": req["fromUserId"]}, {"_id": 0})
        if from_user:
            req["fromUser"] = from_user
    
    for req in outgoing:
        to_user = await db.users.find_one({"id": req["toUserId"]}, {"_id": 0})
        if to_user:
            req["toUser"] = to_user
    
    return incoming + outgoing

@api_router.post("/friend-requests/{requestId}/accept")
async def accept_friend_request(requestId: str):
    """Accept a friend request"""
    request = await db.friend_requests.find_one({"id": requestId}, {"_id": 0})
    if not request:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    if request["status"] != "pending":
        raise HTTPException(status_code=400, detail="Request already processed")
    
    # Update request status
    await db.friend_requests.update_one(
        {"id": requestId},
        {"$set": {"status": "accepted", "decidedAt": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Create friendship with canonical ordering
    u1, u2 = get_canonical_friend_order(request["fromUserId"], request["toUserId"])
    friendship = Friendship(userId1=u1, userId2=u2)
    await db.friendships.insert_one(friendship.model_dump())
    
    # Auto-create DM thread if doesn't exist
    existing_thread = await db.dm_threads.find_one({
        "$or": [
            {"user1Id": request["fromUserId"], "user2Id": request["toUserId"]},
            {"user1Id": request["toUserId"], "user2Id": request["fromUserId"]}
        ]
    }, {"_id": 0})
    
    if not existing_thread:
        dm_thread = DMThread(
            user1Id=u1,
            user2Id=u2
        )
        await db.dm_threads.insert_one(dm_thread.model_dump())
        logging.info(f"Auto-created DM thread {dm_thread.id} for friendship")
    
    # Get users for notification
    to_user = await db.users.find_one({"id": request["toUserId"]}, {"_id": 0})
    from_user = await db.users.find_one({"id": request["fromUserId"]}, {"_id": 0})
    
    # Create notification
    notification = Notification(
        userId=request["fromUserId"],
        type="friend_accepted",
        content=f"{to_user.get('name', 'Someone')} accepted your friend request",
        link=f"/profile/{request['toUserId']}",
        payload={"toUser": to_user}
    )
    await db.notifications.insert_one(notification.model_dump())
    
    # Real-time notifications via WebSocket
    await emit_to_user(request["fromUserId"], 'friend_event', {
        'type': 'accepted',
        'peerId': request["toUserId"],
        'peer': to_user
    })
    await emit_to_user(request["toUserId"], 'friend_event', {
        'type': 'accepted',
        'peerId': request["fromUserId"],
        'peer': from_user
    })
    
    # Award credits
    await earn_credits(request["fromUserId"], 10, "friend", "Friend request accepted")
    await earn_credits(request["toUserId"], 10, "friend", "New friend added")
    
    return {"success": True, "status": "accepted"}

@api_router.post("/friend-requests/{requestId}/reject")
async def reject_friend_request(requestId: str):
    """Reject/decline a friend request"""
    request = await db.friend_requests.find_one({"id": requestId}, {"_id": 0})
    if not request:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    await db.friend_requests.update_one(
        {"id": requestId},
        {"$set": {"status": "declined", "decidedAt": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"success": True, "status": "declined"}

@api_router.post("/friend-requests/{requestId}/cancel")
async def cancel_friend_request(requestId: str):
    """Cancel a sent friend request"""
    request = await db.friend_requests.find_one({"id": requestId}, {"_id": 0})
    if not request:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    if request["status"] != "pending":
        raise HTTPException(status_code=400, detail="Can only cancel pending requests")
    
    await db.friend_requests.update_one(
        {"id": requestId},
        {"$set": {"status": "cancelled", "decidedAt": datetime.now(timezone.utc).isoformat()}}
    )
    
    return {"success": True, "status": "cancelled"}

@api_router.get("/friends/list")
async def get_friends_list(userId: str, q: str = "", cursor: str = "0", limit: int = 50):
    """Get user's friends list with search"""
    # Get all friendships
    friendships = await db.friendships.find({
        "$or": [{"userId1": userId}, {"userId2": userId}]
    }, {"_id": 0}).to_list(1000)
    
    friends = []
    for friendship in friendships:
        friend_id = friendship["userId2"] if friendship["userId1"] == userId else friendship["userId1"]
        friend = await db.users.find_one({"id": friend_id}, {"_id": 0})
        if friend:
            # Apply search filter
            if q:
                if q.lower() in friend.get('name', '').lower() or q.lower() in friend.get('handle', '').lower():
                    friends.append({
                        "user": friend,
                        "friendedAt": friendship.get("createdAt")
                    })
            else:
                friends.append({
                    "user": friend,
                    "friendedAt": friendship.get("createdAt")
                })
    
    # Simple pagination
    start_idx = int(cursor)
    end_idx = start_idx + limit
    paginated_friends = friends[start_idx:end_idx]
    next_cursor = str(end_idx) if end_idx < len(friends) else None
    
    return {
        "items": paginated_friends,
        "nextCursor": next_cursor
    }

@api_router.delete("/friends/{friendUserId}")
async def remove_friend(userId: str, friendUserId: str):
    """Remove a friend (unfriend)"""
    u1, u2 = get_canonical_friend_order(userId, friendUserId)
    
    result = await db.friendships.delete_one({"userId1": u1, "userId2": u2})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Friendship not found")
    
    # Real-time notification
    await emit_to_user(friendUserId, 'friend_event', {
        'type': 'removed',
        'peerId': userId
    })
    
    return {"success": True}

# ===== BLOCK & MUTE ROUTES =====

@api_router.post("/blocks")
async def block_user(blockerId: str, blockedUserId: str):
    """Block a user"""
    if blockerId == blockedUserId:
        raise HTTPException(status_code=400, detail="Cannot block yourself")
    
    # Check if already blocked
    existing = await db.user_blocks.find_one({
        "blockerId": blockerId,
        "blockedId": blockedUserId
    }, {"_id": 0})
    
    if existing:
        return {"success": True, "message": "Already blocked"}
    
    # Create block
    block = UserBlock(blockerId=blockerId, blockedId=blockedUserId)
    await db.user_blocks.insert_one(block.model_dump())
    
    # Remove friendship if exists
    u1, u2 = get_canonical_friend_order(blockerId, blockedUserId)
    await db.friendships.delete_one({"userId1": u1, "userId2": u2})
    
    # Cancel pending friend requests in both directions
    await db.friend_requests.update_many(
        {
            "$or": [
                {"fromUserId": blockerId, "toUserId": blockedUserId},
                {"fromUserId": blockedUserId, "toUserId": blockerId}
            ],
            "status": "pending"
        },
        {"$set": {"status": "cancelled"}}
    )
    
    return {"success": True}

@api_router.delete("/blocks/{blockedUserId}")
async def unblock_user(blockerId: str, blockedUserId: str):
    """Unblock a user"""
    result = await db.user_blocks.delete_one({
        "blockerId": blockerId,
        "blockedId": blockedUserId
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Block not found")
    
    return {"success": True}

@api_router.get("/blocks")
async def get_blocked_users(userId: str):
    """Get list of blocked users"""
    blocks = await db.user_blocks.find({"blockerId": userId}, {"_id": 0}).to_list(1000)
    
    blocked_users = []
    for block in blocks:
        user = await db.users.find_one({"id": block["blockedId"]}, {"_id": 0})
        if user:
            blocked_users.append({
                "user": user,
                "blockedAt": block["createdAt"]
            })
    
    return blocked_users

@api_router.post("/mutes")
async def mute_user(muterId: str, mutedUserId: str):
    """Mute a user (silence notifications)"""
    if muterId == mutedUserId:
        raise HTTPException(status_code=400, detail="Cannot mute yourself")
    
    # Check if already muted
    existing = await db.user_mutes.find_one({
        "muterId": muterId,
        "mutedId": mutedUserId
    }, {"_id": 0})
    
    if existing:
        return {"success": True, "message": "Already muted"}
    
    # Create mute
    mute = UserMute(muterId=muterId, mutedId=mutedUserId)
    await db.user_mutes.insert_one(mute.model_dump())
    
    return {"success": True}

@api_router.delete("/mutes/{mutedUserId}")
async def unmute_user(muterId: str, mutedUserId: str):
    """Unmute a user"""
    result = await db.user_mutes.delete_one({
        "muterId": muterId,
        "mutedId": mutedUserId
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Mute not found")
    
    return {"success": True}

@api_router.get("/mutes")
async def get_muted_users(userId: str):
    """Get list of muted users"""
    mutes = await db.user_mutes.find({"muterId": userId}, {"_id": 0}).to_list(1000)
    
    muted_users = []
    for mute in mutes:
        user = await db.users.find_one({"id": mute["mutedId"]}, {"_id": 0})
        if user:
            muted_users.append({
                "user": user,
                "mutedAt": mute["createdAt"]
            })
    
    return muted_users

# ===== DIRECT MESSAGING (DM) ROUTES =====

@api_router.get("/dm/threads")
async def get_dm_threads(userId: str, cursor: str = "0", limit: int = 50):
    """Get user's DM threads with last message and unread count"""
    # Find all threads where user is participant
    threads = await db.dm_threads.find({
        "$or": [{"user1Id": userId}, {"user2Id": userId}]
    }, {"_id": 0}).sort("lastMessageAt", -1).to_list(1000)
    
    result = []
    for thread in threads:
        # Get peer user
        peer_id = thread["user2Id"] if thread["user1Id"] == userId else thread["user1Id"]
        peer = await db.users.find_one({"id": peer_id}, {"_id": 0})
        
        if not peer:
            continue
        
        # Get last message
        # Get last message (newest)
        last_message_cursor = db.messages.find(
            {"threadId": thread["id"], "deletedAt": None},
            {"_id": 0}
        ).sort("createdAt", -1).limit(1)
        last_message_docs = await last_message_cursor.to_list(length=1)
        last_message = last_message_docs[0] if last_message_docs else None
        
        # Get unread count
        read_receipt = await db.message_reads.find_one({
            "threadId": thread["id"],
            "userId": userId
        }, {"_id": 0})
        
        last_read_id = read_receipt.get("lastReadMessageId") if read_receipt else None
        
        if last_read_id:
            unread_count = await db.messages.count_documents({
                "threadId": thread["id"],
                "senderId": {"$ne": userId},
                "createdAt": {"$gt": last_message.get("createdAt") if last_message else ""},
                "deletedAt": None
            })
        else:
            unread_count = await db.messages.count_documents({
                "threadId": thread["id"],
                "senderId": {"$ne": userId},
                "deletedAt": None
            })
        
        result.append({
            "id": thread["id"],
            "peer": peer,
            "lastMessage": last_message,
            "unreadCount": unread_count,
            "updatedAt": thread.get("lastMessageAt", thread["createdAt"])
        })
    
    # Pagination
    start_idx = int(cursor)
    end_idx = start_idx + limit
    paginated = result[start_idx:end_idx]
    next_cursor = str(end_idx) if end_idx < len(result) else None
    
    return {"items": paginated, "nextCursor": next_cursor}

@api_router.post("/dm/thread")
async def create_or_get_dm_thread(userId: str, peerUserId: str):
    """Create or get existing DM thread with another user"""
    if userId == peerUserId:
        raise HTTPException(status_code=400, detail="Cannot create thread with yourself")
    
    # Check if either user blocked the other
    if await is_blocked(userId, peerUserId) or await is_blocked(peerUserId, userId):
        raise HTTPException(status_code=403, detail="Cannot message this user")
    
    # Check if friends (required for DM)
    friends = await are_friends(userId, peerUserId)
    
    # Find existing thread
    existing_thread = await db.dm_threads.find_one({
        "$or": [
            {"user1Id": userId, "user2Id": peerUserId},
            {"user1Id": peerUserId, "user2Id": userId}
        ]
    }, {"_id": 0})
    
    if existing_thread:
        return {"threadId": existing_thread["id"], "existing": True}
    
    # Create new thread only if friends
    if not friends:
        raise HTTPException(status_code=403, detail="Must be friends to start a conversation")
    
    u1, u2 = get_canonical_friend_order(userId, peerUserId)
    thread = DMThread(user1Id=u1, user2Id=u2)
    await db.dm_threads.insert_one(thread.model_dump())
    
    return {"threadId": thread.id, "existing": False}

@api_router.get("/dm/threads/{threadId}/messages")
async def get_thread_messages(threadId: str, userId: str, cursor: str = "", limit: int = 50):
    """Get messages from a thread"""
    # Verify user is participant
    thread = await db.dm_threads.find_one({"id": threadId}, {"_id": 0})
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if userId not in [thread["user1Id"], thread["user2Id"]]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get messages
    query = {"threadId": threadId, "deletedAt": None}
    if cursor:
        query["createdAt"] = {"$lt": cursor}
    
    messages = await db.messages.find(query, {"_id": 0}).sort("createdAt", -1).limit(limit).to_list(limit)
    messages.reverse()  # Return in chronological order
    
    next_cursor = messages[0]["createdAt"] if messages else None
    
    return {"items": messages, "nextCursor": next_cursor}

class SendMessageInput(BaseModel):
    text: Optional[str] = None
    mediaUrl: Optional[str] = None
    mimeType: Optional[str] = None


@api_router.post("/dm/threads/{threadId}/messages")
async def send_message(threadId: str, userId: str, payload: SendMessageInput = Body(...)):
    """Send a message in a thread"""
    # Verify thread exists and user is participant
    thread = await db.dm_threads.find_one({"id": threadId}, {"_id": 0})
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    if userId not in [thread["user1Id"], thread["user2Id"]]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get peer
    peer_id = thread["user2Id"] if thread["user1Id"] == userId else thread["user1Id"]
    
    # Check if blocked
    if await is_blocked(userId, peer_id) or await is_blocked(peer_id, userId):
        raise HTTPException(status_code=403, detail="Cannot send message")
    
    # Validate content
    if not payload.text and not payload.mediaUrl:
        raise HTTPException(status_code=400, detail="Message must have text or media")
    
    # Create message
    message = DMMessage(
        threadId=threadId,
        senderId=userId,
        text=payload.text,
        mediaUrl=payload.mediaUrl,
        mimeType=payload.mimeType
    )
    await db.messages.insert_one(message.model_dump())
    
    # Update thread's lastMessageAt
    await db.dm_threads.update_one(
        {"id": threadId},
        {"$set": {"lastMessageAt": message.createdAt}}
    )
    
    # Real-time: emit to thread participants
    sender = await db.users.find_one({"id": userId}, {"_id": 0})
    await emit_to_thread(threadId, 'message', {
        "type": "message",
        "message": {
            **message.model_dump(),
            "sender": sender
        }
    }, exclude_user=userId)
    
    # Check if peer is muted
    is_muted = await db.user_mutes.find_one({
        "muterId": peer_id,
        "mutedId": userId
    }, {"_id": 0})
    
    # Create notification if not muted
    if not is_muted:
        notification = Notification(
            userId=peer_id,
            type="dm",
            content=payload.text[:50] if payload.text else "Sent a photo",
            link=f"/messenger/{threadId}",
            payload={"sender": sender, "threadId": threadId}
        )
        await db.notifications.insert_one(notification.model_dump())
    
    return {"messageId": message.id, "timestamp": message.createdAt}

@api_router.post("/dm/threads/{threadId}/read")
async def mark_thread_read(threadId: str, userId: str, lastReadMessageId: str):
    """Mark messages as read"""
    # Verify thread and user
    thread = await db.dm_threads.find_one({"id": threadId}, {"_id": 0})
    if not thread or userId not in [thread["user1Id"], thread["user2Id"]]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update or create read receipt
    await db.message_reads.update_one(
        {"threadId": threadId, "userId": userId},
        {
            "$set": {
                "lastReadMessageId": lastReadMessageId,
                "readAt": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    
    # Real-time: emit read receipt to peer
    await emit_to_thread(threadId, 'read', {
        "type": "read",
        "userId": userId,
        "lastReadMessageId": lastReadMessageId,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }, exclude_user=userId)
    
    return {"success": True}

@api_router.patch("/dm/messages/{messageId}")
async def edit_message(messageId: str, userId: str, text: str):
    """Edit a message"""
    message = await db.messages.find_one({"id": messageId}, {"_id": 0})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message["senderId"] != userId:
        raise HTTPException(status_code=403, detail="Can only edit your own messages")
    
    if message.get("deletedAt"):
        raise HTTPException(status_code=400, detail="Cannot edit deleted message")
    
    await db.messages.update_one(
        {"id": messageId},
        {"$set": {
            "text": text,
            "editedAt": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    # Real-time: emit edit to thread
    updated_message = await db.messages.find_one({"id": messageId}, {"_id": 0})
    await emit_to_thread(message["threadId"], 'message_edited', {
        "type": "edit",
        "message": updated_message
    })
    
    return {"success": True}

@api_router.delete("/dm/messages/{messageId}")
async def delete_message(messageId: str, userId: str):
    """Soft delete a message"""
    message = await db.messages.find_one({"id": messageId}, {"_id": 0})
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if message["senderId"] != userId:
        raise HTTPException(status_code=403, detail="Can only delete your own messages")
    
    await db.messages.update_one(
        {"id": messageId},
        {"$set": {"deletedAt": datetime.now(timezone.utc).isoformat()}}
    )
    
    # Real-time: emit deletion to thread
    await emit_to_thread(message["threadId"], 'message_deleted', {
        "type": "delete",
        "messageId": messageId
    })
    
    return {"success": True}

@api_router.get("/friends/{userId}")
async def get_friends(userId: str):
    """Get user's friends list"""
    friendships = await db.friendships.find({
        "$or": [{"userId1": userId}, {"userId2": userId}]
    }, {"_id": 0}).to_list(1000)
    
    friends = []
    for friendship in friendships:
        friend_id = friendship["userId2"] if friendship["userId1"] == userId else friendship["userId1"]
        friend = await db.users.find_one({"id": friend_id}, {"_id": 0})
        if friend:
            friends.append(friend)
    
    return friends

@api_router.get("/friends/check/{userId}/{friendId}")
async def check_friendship(userId: str, friendId: str):
    """Check if two users are friends"""
    friendship = await db.friendships.find_one({
        "$or": [
            {"userId1": userId, "userId2": friendId},
            {"userId1": friendId, "userId2": userId}
        ]
    }, {"_id": 0})
    
    if friendship:
        return {"areFriends": True}
    
    # Check for pending request
    pending_request = await db.friend_requests.find_one({
        "$or": [
            {"fromUserId": userId, "toUserId": friendId},
            {"fromUserId": friendId, "toUserId": userId}
        ],
        "status": "pending"
    }, {"_id": 0})
    
    if pending_request:
        return {
            "areFriends": False,
            "hasPendingRequest": True,
            "requestDirection": "sent" if pending_request["fromUserId"] == userId else "received"
        }
    
    return {"areFriends": False, "hasPendingRequest": False}

    analytics["creditsBalance"] = credits_info["balance"]
    
    # Calculate tier based on credits
    balance = credits_info["balance"]
    if balance >= 10000:
        tier = "Platinum"
    elif balance >= 5000:
        tier = "Gold"
    elif balance >= 1000:
        tier = "Silver"
    else:
        tier = "Bronze"
    
    analytics["tier"] = tier
    
    # Update tier in database
    await db.user_analytics.update_one(
        {"userId": userId},
        {"$set": {"tier": tier}}
    )
    
    return analytics

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()