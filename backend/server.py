from fastapi import FastAPI, APIRouter, HTTPException, Body, UploadFile, File, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
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

# Create uploads directory
UPLOAD_DIR = Path("/app/backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Serve uploaded files as static
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

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
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class TopUpRequest(BaseModel):
    amount: float

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

class Friendship(BaseModel):
    model_config = ConfigDict(extra="ignore")
    userId1: str
    userId2: str
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

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

# ===== AUTH ROUTES (REAL AUTHENTICATION WITH GOOGLE SHEETS) =====

@api_router.post("/auth/signup", response_model=dict)
async def signup(req: UserCreate):
    """
    Register a new user with email and password.
    User data is stored in Google Sheets (or demo mode).
    """
    try:
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
            name=req.name
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
                "email": user['email']
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

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
            name=user['name']
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

# ===== ANALYTICS ROUTES =====

@api_router.get("/analytics/{userId}")
async def get_user_analytics(userId: str):
    """Get user analytics dashboard"""
    analytics = await db.user_analytics.find_one({"userId": userId}, {"_id": 0})
    if not analytics:
        analytics = UserAnalytics(userId=userId).model_dump()
        await db.user_analytics.insert_one(analytics)
    
    # Get credits balance
    credits_info = await get_user_credits(userId)


# ===== FRIEND REQUEST ROUTES =====

@api_router.post("/friend-requests")
async def send_friend_request(fromUserId: str, toUserId: str):
    """Send a friend request"""
    # Check if already friends
    existing_friendship = await db.friendships.find_one({
        "$or": [
            {"userId1": fromUserId, "userId2": toUserId},
            {"userId1": toUserId, "userId2": fromUserId}
        ]
    })
    if existing_friendship:
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
    
    # Create notification
    from_user = await db.users.find_one({"id": fromUserId}, {"_id": 0})
    notification = Notification(
        userId=toUserId,
        type="friend_request",
        content=f"{from_user.get('name', 'Someone')} sent you a friend request",
        link=f"/profile/{fromUserId}"
    )
    await db.notifications.insert_one(notification.model_dump())
    
    return {"success": True, "request": friend_request.model_dump()}

@api_router.get("/friend-requests/{userId}")
async def get_friend_requests(userId: str):
    """Get incoming friend requests"""
    requests = await db.friend_requests.find({
        "toUserId": userId,
        "status": "pending"
    }, {"_id": 0}).to_list(100)
    
    # Enrich with user data
    for req in requests:
        from_user = await db.users.find_one({"id": req["fromUserId"]}, {"_id": 0})
        if from_user:
            req["fromUser"] = from_user
    
    return requests

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
        {"$set": {"status": "accepted"}}
    )
    
    # Create friendship
    friendship = Friendship(
        userId1=request["fromUserId"],
        userId2=request["toUserId"]
    )
    await db.friendships.insert_one(friendship.model_dump())
    
    # Create notification
    to_user = await db.users.find_one({"id": request["toUserId"]}, {"_id": 0})
    notification = Notification(
        userId=request["fromUserId"],
        type="friend_accept",
        content=f"{to_user.get('name', 'Someone')} accepted your friend request",
        link=f"/profile/{request['toUserId']}"
    )
    await db.notifications.insert_one(notification.model_dump())
    
    # Award credits
    await earn_credits(request["fromUserId"], 10, "friend", "Friend request accepted")
    await earn_credits(request["toUserId"], 10, "friend", "New friend added")
    
    return {"success": True}

@api_router.post("/friend-requests/{requestId}/reject")
async def reject_friend_request(requestId: str):
    """Reject a friend request"""
    request = await db.friend_requests.find_one({"id": requestId}, {"_id": 0})
    if not request:
        raise HTTPException(status_code=404, detail="Friend request not found")
    
    await db.friend_requests.update_one(
        {"id": requestId},
        {"$set": {"status": "rejected"}}
    )
    
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