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
    language: str = "en"
    interests: List[str] = Field(default_factory=list)
    consentGiven: bool = False
    walletBalance: float = 0.0
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserCreate(BaseModel):
    handle: str
    name: str
    password: str

class LoginRequest(BaseModel):
    handle: str
    password: str

class OnboardingData(BaseModel):
    language: str = "en"
    interests: List[str] = []
    consentGiven: bool = True

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
    flagged: bool = False
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
    isLive: bool = False
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

class Order(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    userId: str
    venueId: str
    items: List[dict] = Field(default_factory=list)
    total: float = 0.0
    split: List[dict] = Field(default_factory=list)
    status: str = "pending"  # pending, confirmed, preparing, ready, completed
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class OrderCreate(BaseModel):
    venueId: str
    items: List[dict]
    total: float
    split: List[dict] = []

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

class Ticket(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    eventId: str
    purchaserId: str
    tier: str = "General"
    price: float = 0.0
    qrToken: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "active"
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class TicketPurchase(BaseModel):
    eventId: str
    tier: str
    price: float

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

# ===== AUTH ROUTES =====

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

@api_router.post("/auth/onboarding")
async def complete_onboarding(userId: str, data: OnboardingData):
    await db.users.update_one(
        {"id": userId},
        {"$set": {
            "language": data.language,
            "interests": data.interests,
            "consentGiven": data.consentGiven
        }}
    )
    return {"success": True}

# ===== USER ROUTES =====

@api_router.get("/users/{userId}")
async def get_user(userId: str):
    user = await db.users.find_one({"id": userId}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ===== POST ROUTES =====

@api_router.get("/posts")
async def get_posts(limit: int = 50):
    posts = await db.posts.find({}, {"_id": 0}).sort("createdAt", -1).to_list(limit)
    for post in posts:
        author = await db.users.find_one({"id": post["authorId"]}, {"_id": 0})
        post["author"] = author if author else None
    return posts

@api_router.post("/posts")
async def create_post(post: PostCreate, authorId: str):
    post_obj = Post(authorId=authorId, **post.model_dump())
    doc = post_obj.model_dump()
    result = await db.posts.insert_one(doc)
    doc.pop('_id', None)
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
    result = await db.comments.insert_one(doc)
    doc.pop('_id', None)
    
    await db.posts.update_one({"id": postId}, {"$inc": {"stats.replies": 1}})
    
    author = await db.users.find_one({"id": authorId}, {"_id": 0})
    doc["author"] = author
    return doc

# ===== REEL ROUTES =====

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
    tribe = await db.tribes.find_one({"id": tribeId}, {"_id": 0})
    if not tribe:
        raise HTTPException(status_code=404, detail="Tribe not found")
    
    posts = await db.posts.find({"authorId": {"$in": tribe.get("members", [])}}, {"_id": 0}).sort("createdAt", -1).to_list(limit)
    for post in posts:
        author = await db.users.find_one({"id": post["authorId"]}, {"_id": 0})
        post["author"] = author
    return posts

# ===== MESSAGE ROUTES =====

@api_router.get("/messages")
async def get_user_messages(userId: str):
    messages = await db.messages.find({
        "$or": [{"fromId": userId}, {"toId": userId}]
    }, {"_id": 0}).sort("createdAt", -1).to_list(1000)
    
    # Enrich with user data
    for msg in messages:
        if msg["fromId"] != userId:
            peer = await db.users.find_one({"id": msg["fromId"]}, {"_id": 0})
            msg["peer"] = peer
        else:
            peer = await db.users.find_one({"id": msg["toId"]}, {"_id": 0})
            msg["peer"] = peer
    
    return messages

@api_router.get("/messages/thread")
async def get_thread(userId: str, peerId: str):
    messages = await db.messages.find({
        "$or": [
            {"fromId": userId, "toId": peerId},
            {"fromId": peerId, "toId": userId}
        ]
    }, {"_id": 0}).sort("createdAt", 1).to_list(1000)
    
    return messages

@api_router.post("/messages")
async def send_message(msg: MessageCreate, fromId: str, toId: str):
    message_obj = Message(fromId=fromId, toId=toId, text=msg.text)
    doc = message_obj.model_dump()
    result = await db.messages.insert_one(doc)
    doc.pop('_id', None)
    
    # Create notification
    notif = Notification(
        userId=toId,
        type="dm",
        payload={"fromId": fromId, "text": msg.text[:50]}
    )
    await db.notifications.insert_one(notif.model_dump())
    
    return doc

# ===== NOTIFICATION ROUTES =====

@api_router.get("/notifications")
async def get_notifications(userId: str):
    notifs = await db.notifications.find({"userId": userId}, {"_id": 0}).sort("createdAt", -1).to_list(100)
    return notifs

@api_router.post("/notifications/{notifId}/read")
async def mark_notification_read(notifId: str):
    await db.notifications.update_one({"id": notifId}, {"$set": {"read": True}})
    return {"success": True}

# ===== VENUE & ORDER ROUTES =====

@api_router.get("/venues")
async def get_venues():
    venues = await db.venues.find({}, {"_id": 0}).to_list(100)
    return venues

@api_router.get("/venues/{venueId}")
async def get_venue(venueId: str):
    venue = await db.venues.find_one({"id": venueId}, {"_id": 0})
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return venue

@api_router.post("/orders")
async def create_order(order: OrderCreate, userId: str):
    order_obj = Order(userId=userId, **order.model_dump())
    doc = order_obj.model_dump()
    result = await db.orders.insert_one(doc)
    doc.pop('_id', None)
    
    # Create notification
    notif = Notification(
        userId=userId,
        type="order_placed",
        payload={"orderId": order_obj.id, "total": order.total}
    )
    await db.notifications.insert_one(notif.model_dump())
    
    return doc

@api_router.get("/orders")
async def get_user_orders(userId: str):
    orders = await db.orders.find({"userId": userId}, {"_id": 0}).sort("createdAt", -1).to_list(100)
    return orders

# ===== EVENT & TICKET ROUTES =====

@api_router.get("/events")
async def get_events():
    events = await db.events.find({}, {"_id": 0}).to_list(100)
    return events

@api_router.get("/events/{eventId}")
async def get_event(eventId: str):
    event = await db.events.find_one({"id": eventId}, {"_id": 0})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@api_router.post("/tickets")
async def purchase_ticket(ticket: TicketPurchase, userId: str):
    ticket_obj = Ticket(purchaserId=userId, **ticket.model_dump())
    doc = ticket_obj.model_dump()
    result = await db.tickets.insert_one(doc)
    doc.pop('_id', None)
    
    # Create notification
    notif = Notification(
        userId=userId,
        type="ticket_bought",
        payload={"ticketId": ticket_obj.id, "eventId": ticket.eventId}
    )
    await db.notifications.insert_one(notif.model_dump())
    
    return doc

@api_router.get("/tickets")
async def get_user_tickets(userId: str):
    tickets = await db.tickets.find({"purchaserId": userId}, {"_id": 0}).to_list(100)
    
    # Enrich with event data
    for ticket in tickets:
        event = await db.events.find_one({"id": ticket["eventId"]}, {"_id": 0})
        ticket["event"] = event
    
    return tickets

# ===== CREATOR ROUTES =====

@api_router.get("/creators")
async def get_creators():
    creators = await db.creators.find({}, {"_id": 0}).to_list(100)
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

# ===== SEARCH ROUTES =====

@api_router.get("/search")
async def search(q: str, filter: str = "all"):
    results = {"posts": [], "tribes": [], "venues": [], "events": [], "creators": []}
    
    if filter in ["all", "posts"]:
        posts = await db.posts.find(
            {"text": {"$regex": q, "$options": "i"}},
            {"_id": 0}
        ).limit(20).to_list(20)
        for post in posts:
            author = await db.users.find_one({"id": post["authorId"]}, {"_id": 0})
            post["author"] = author
        results["posts"] = posts
    
    if filter in ["all", "tribes"]:
        tribes = await db.tribes.find(
            {"$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"tags": {"$regex": q, "$options": "i"}}
            ]},
            {"_id": 0}
        ).limit(20).to_list(20)
        results["tribes"] = tribes
    
    if filter in ["all", "venues"]:
        venues = await db.venues.find(
            {"name": {"$regex": q, "$options": "i"}},
            {"_id": 0}
        ).limit(20).to_list(20)
        results["venues"] = venues
    
    if filter in ["all", "events"]:
        events = await db.events.find(
            {"name": {"$regex": q, "$options": "i"}},
            {"_id": 0}
        ).limit(20).to_list(20)
        results["events"] = events
    
    if filter in ["all", "creators"]:
        creators = await db.creators.find(
            {"displayName": {"$regex": q, "$options": "i"}},
            {"_id": 0}
        ).limit(20).to_list(20)
        results["creators"] = creators
    
    return results

# ===== SEED DATA ROUTE =====

@api_router.post("/seed/full")
async def seed_full_data():
    # Clear existing data
    await db.users.delete_many({})
    await db.posts.delete_many({})
    await db.reels.delete_many({})
    await db.tribes.delete_many({})
    await db.comments.delete_many({})
    await db.messages.delete_many({})
    await db.notifications.delete_many({})
    await db.venues.delete_many({})
    await db.orders.delete_many({})
    await db.events.delete_many({})
    await db.tickets.delete_many({})
    await db.creators.delete_many({})
    await db.wallet_transactions.delete_many({})
    
    # Seed users (from previous seed)
    users = [
        {"id": "u1", "handle": "vibekween", "name": "Priya Sharma", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=priya", "bio": "Free speech advocate | Coffee addict ☕", "kycTier": 2, "walletBalance": 500.0, "language": "en", "interests": ["tech", "society"], "consentGiven": True, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u2", "handle": "techbro_raj", "name": "Raj Malhotra", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=raj", "bio": "Building in public 🚀", "kycTier": 1, "walletBalance": 1000.0, "language": "en", "interests": ["tech", "startups"], "consentGiven": True, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u3", "handle": "artsy_soul", "name": "Ananya Reddy", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=ananya", "bio": "Digital artist | Vibe curator 🎨", "kycTier": 1, "walletBalance": 750.0, "language": "en", "interests": ["art", "design"], "consentGiven": True, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u4", "handle": "crypto_maya", "name": "Maya Patel", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=maya", "bio": "Web3 enthusiast | HODL 💎", "kycTier": 3, "walletBalance": 2500.0, "language": "en", "interests": ["crypto", "web3"], "consentGiven": True, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "u5", "handle": "foodie_sahil", "name": "Sahil Khan", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=sahil", "bio": "Food blogger | Mumbai's best eats 🍕", "kycTier": 1, "walletBalance": 300.0, "language": "en", "interests": ["food", "travel"], "consentGiven": True, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "demo_user", "handle": "demo", "name": "Demo User", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=demo", "bio": "Testing Loopync! 🎉", "kycTier": 1, "walletBalance": 1500.0, "language": "en", "interests": ["tech", "social"], "consentGiven": True, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.users.insert_many(users)
    
    # Seed posts (from previous)
    posts = [
        {"id": "p1", "authorId": "u1", "text": "Free speech doesn't mean freedom from consequences, but it does mean freedom to speak. Let's normalize respectful disagreement! 🗣️", "media": None, "audience": "public", "stats": {"likes": 42, "quotes": 5, "reposts": 12, "replies": 8}, "likedBy": ["u2", "u3"], "repostedBy": ["u4"], "flagged": False, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "p2", "authorId": "u2", "text": "Just launched my new side project! Built with React + FastAPI. Ship fast, iterate faster 🚀", "media": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800", "audience": "public", "stats": {"likes": 89, "quotes": 3, "reposts": 22, "replies": 15}, "likedBy": ["u1", "u3", "u5"], "repostedBy": [], "flagged": False, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "p3", "authorId": "u3", "text": "New artwork drop! Exploring neon aesthetics and cyber themes. What do you think? 💫", "media": "https://images.unsplash.com/photo-1634973357973-f2ed2657db3c?w=800", "audience": "public", "stats": {"likes": 156, "quotes": 8, "reposts": 34, "replies": 22}, "likedBy": ["u1", "u2", "u4", "u5"], "repostedBy": ["u1"], "flagged": False, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.posts.insert_many(posts)
    
    # Seed reels
    reels = [
        {"id": "r1", "authorId": "u1", "videoUrl": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4", "thumb": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=400", "caption": "Morning vibe check ☀️ #MumbaiLife", "stats": {"views": 2341, "likes": 456, "comments": 34}, "likedBy": ["u2", "u3"], "isLive": False, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "r2", "authorId": "u3", "videoUrl": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4", "thumb": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=400", "caption": "New digital art process 🎨✨", "stats": {"views": 5678, "likes": 892, "comments": 67}, "likedBy": ["u1", "u2", "u4"], "isLive": False, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.reels.insert_many(reels)
    
    # Seed tribes
    tribes = [
        {"id": "t1", "name": "Tech Builders India", "tags": ["tech", "startups", "coding"], "type": "public", "description": "A community for builders, makers, and tech enthusiasts across India.", "avatar": "https://api.dicebear.com/7.x/shapes/svg?seed=tech", "ownerId": "u2", "members": ["u2", "u1", "u4"], "memberCount": 3, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "t2", "name": "Digital Artists Hub", "tags": ["art", "design", "nft"], "type": "public", "description": "Share your art, get feedback, collaborate on projects.", "avatar": "https://api.dicebear.com/7.x/shapes/svg?seed=art", "ownerId": "u3", "members": ["u3", "u1"], "memberCount": 2, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "t3", "name": "Web3 India", "tags": ["crypto", "blockchain", "web3"], "type": "public", "description": "India's premier Web3 community. Learn, build, and grow together.", "avatar": "https://api.dicebear.com/7.x/shapes/svg?seed=web3", "ownerId": "u4", "members": ["u4", "u2"], "memberCount": 2, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "t4", "name": "Mumbai Foodies", "tags": ["food", "mumbai", "restaurants"], "type": "public", "description": "Best food spots in Mumbai. Reviews, recommendations, and more!", "avatar": "https://api.dicebear.com/7.x/shapes/svg?seed=food", "ownerId": "u5", "members": ["u5", "u1", "u3", "demo_user"], "memberCount": 4, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.tribes.insert_many(tribes)
    
    # Seed venues
    venues = [
        {"id": "v1", "name": "Café Mondegar", "description": "Iconic café in Colaba with vintage vibes", "avatar": "https://api.dicebear.com/7.x/shapes/svg?seed=cafe1", "location": "Colaba, Mumbai", "rating": 4.5, "menuItems": [{"id": "m1", "name": "Cappuccino", "price": 150}, {"id": "m2", "name": "Chicken Sandwich", "price": 250}, {"id": "m3", "name": "Chocolate Cake", "price": 180}], "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "v2", "name": "The Bombay Canteen", "description": "Modern Indian cuisine with a twist", "avatar": "https://api.dicebear.com/7.x/shapes/svg?seed=restaurant1", "location": "Lower Parel, Mumbai", "rating": 4.8, "menuItems": [{"id": "m4", "name": "Butter Chicken", "price": 450}, {"id": "m5", "name": "Naan", "price": 80}, {"id": "m6", "name": "Masala Chai", "price": 100}], "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.venues.insert_many(venues)
    
    # Seed events
    events = [
        {"id": "e1", "name": "TechCrunch Disrupt Mumbai", "description": "India's biggest tech conference", "image": "https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800", "date": "2025-11-15", "location": "BKC, Mumbai", "tiers": [{"name": "General", "price": 5000}, {"name": "VIP", "price": 15000}], "vibeMeter": 92, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "e2", "name": "Mumbai Food Festival", "description": "Explore the best street food Mumbai has to offer", "image": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800", "date": "2025-11-22", "location": "Juhu Beach, Mumbai", "tiers": [{"name": "Entry", "price": 500}], "vibeMeter": 88, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.events.insert_many(events)
    
    # Seed creators
    creators = [
        {"id": "c1", "userId": "u3", "displayName": "Ananya Reddy", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=ananya", "bio": "Digital art courses & NFT masterclasses", "items": [{"id": "i1", "name": "Digital Art Basics", "type": "course", "price": 2999}, {"id": "i2", "name": "NFT Creation Guide", "type": "course", "price": 4999}], "followers": 12400, "createdAt": datetime.now(timezone.utc).isoformat()},
        {"id": "c2", "userId": "u2", "displayName": "Raj Malhotra", "avatar": "https://api.dicebear.com/7.x/avataaars/svg?seed=raj", "bio": "Full-stack development bootcamp", "items": [{"id": "i3", "name": "React Masterclass", "type": "course", "price": 3999}, {"id": "i4", "name": "FastAPI Pro", "type": "course", "price": 2999}], "followers": 8900, "createdAt": datetime.now(timezone.utc).isoformat()},
    ]
    await db.creators.insert_many(creators)
    
    return {
        "message": "Full data seeded successfully",
        "users": len(users),
        "posts": len(posts),
        "reels": len(reels),
        "tribes": len(tribes),
        "venues": len(venues),
        "events": len(events),
        "creators": len(creators)
    }

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
