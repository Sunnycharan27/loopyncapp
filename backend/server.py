from fastapi import FastAPI, APIRouter, HTTPException, Body
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# ===== MODELS =====

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    handle: str
    name: str
    avatar: str = "https://api.dicebear.com/7.x/avataaars/svg?seed=default"
    bio: str = ""
    kycTier: int = 1
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserCreate(BaseModel):
    handle: str
    name: str
    password: str

class LoginRequest(BaseModel):
    handle: str
    password: str

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

# ===== AUTH ROUTES (MOCK) =====

@api_router.post("/auth/login")
async def login(req: LoginRequest):
    user = await db.users.find_one({"handle": req.handle}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"token": f"mock_token_{user['id']}", "user": user}

@api_router.post("/auth/signup")
async def signup(req: UserCreate):
    existing = await db.users.find_one({"handle": req.handle}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Handle already taken")
    
    user_obj = User(handle=req.handle, name=req.name)
    doc = user_obj.model_dump()
    await db.users.insert_one(doc)
    return {"token": f"mock_token_{user_obj.id}", "user": doc}

@api_router.get("/auth/me")
async def get_me(userId: str):
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

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
    return comments

@api_router.post("/posts/{postId}/comments")
async def create_post_comment(postId: str, comment: CommentCreate, authorId: str):
    comment_obj = Comment(postId=postId, authorId=authorId, text=comment.text)
    doc = comment_obj.model_dump()
    await db.comments.insert_one(doc)
    
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
    await db.comments.insert_one(doc)
    
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
    await db.tribes.insert_one(doc)
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
    
    # Seed users
    users = [
        {"id": "u1", "handle": "vibekween", "name": "Priya Sharma", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=priya", "bio": "Free speech advocate | Coffee addict ☕", "kycTier": 2, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u2", "handle": "techbro_raj", "name": "Raj Malhotra", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=raj", "bio": "Building in public 🚀", "kycTier": 1, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u3", "handle": "artsy_soul", "name": "Ananya Reddy", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=ananya", "bio": "Digital artist | Vibe curator 🎨", "kycTier": 1, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u4", "handle": "crypto_maya", "name": "Maya Patel", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=maya", "bio": "Web3 enthusiast | HODL 💎", "kycTier": 3, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u5", "handle": "foodie_sahil", "name": "Sahil Khan", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=sahil", "bio": "Food blogger | Mumbai's best eats 🍕", "kycTier": 1, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "demo_user", "handle": "demo", "name": "Demo User", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=demo", "bio": "Testing Loopync! 🎉", "kycTier": 1, "createdAt": datetime.now(timezone.utc).isoformat()},
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
    
    return {"message": "Data seeded successfully", "users": len(users), "posts": len(posts), "reels": len(reels), "tribes": len(tribes)}

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