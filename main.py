from pathlib import Path
from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.config import settings
from app.db import Base, engine, get_db
from app.models import User, Video, ViewEvent, MonetizationProfile, Like, Comment, Subscription, AdCampaign, AdEvent
from app.schemas import RegisterIn, LoginIn, TokenOut, UserOut, VideoOut, CommentIn, MonetizationReviewIn, AdCampaignIn
from app.security import hash_password, verify_password, create_access_token
from app.dependencies import current_user, admin_user

Base.metadata.create_all(bind=engine)
app = FastAPI(title=settings.app_name, version="0.2.0")

@app.get("/health")
def health():
    return {"service": "chitra-api", "status": "ok", "version": "0.2.0"}

@app.post("/auth/register", response_model=UserOut, status_code=201)
def register(data: RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(409, "Email already registered")
    user = User(email=email, display_name=data.display_name, password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    db.add(MonetizationProfile(creator_id=user.id)); db.commit()
    return user

@app.post("/auth/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password")
    return TokenOut(access_token=create_access_token(str(user.id)))

@app.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user

@app.post("/videos/upload", response_model=VideoOut, status_code=201)
async def upload_video(title: str, description: str = "", is_short: bool = False,
                       duration_seconds: int = 0, file: UploadFile = File(...),
                       db: Session = Depends(get_db), user: User = Depends(current_user)):
    if duration_seconds <= 0 or duration_seconds > 43200:
        raise HTTPException(422, "Duration must be between 1 second and 12 hours")
    if is_short and duration_seconds > 120:
        raise HTTPException(422, "Chitra Shorts must be 120 seconds or shorter")
    allowed = {"video/mp4", "video/quicktime", "video/webm"}
    if file.content_type not in allowed:
        raise HTTPException(415, "Supported upload types: MP4, MOV, WEBM")
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "upload.mp4").suffix[:10] or ".mp4"
    dest = upload_dir / f"{uuid4().hex}{suffix}"
    size = 0
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > settings.max_upload_mb * 1024 * 1024:
                dest.unlink(missing_ok=True)
                raise HTTPException(413, "Upload exceeds configured size limit")
            out.write(chunk)
    video = Video(creator_id=user.id, title=title[:150], description=description[:5000],
                  duration_seconds=duration_seconds, is_short=is_short,
                  source_path=str(dest), status="pending_review")
    db.add(video); db.commit(); db.refresh(video)
    return video

@app.get("/feed", response_model=list[VideoOut])
def feed(limit: int = 20, db: Session = Depends(get_db)):
    limit = max(1, min(limit, 50))
    return list(db.scalars(select(Video).where(Video.status == "published").order_by(Video.created_at.desc()).limit(limit)))

@app.get("/creators/{creator_id}/videos", response_model=list[VideoOut])
def creator_videos(creator_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(Video).where(Video.creator_id == creator_id, Video.status == "published").order_by(Video.created_at.desc()).limit(50)))

@app.post("/videos/{video_id}/view")
def record_view(video_id: int, db: Session = Depends(get_db)):
    video = db.get(Video, video_id)
    if not video or video.status != "published":
        raise HTTPException(404, "Video not available")
    db.add(ViewEvent(video_id=video.id, qualified=False)); db.commit()
    return {"video_id": video_id, "recorded": True, "creator_credit": 0,
            "note": "Raw views do not generate earnings. Only validated, billable ad events can enter settlement."}

@app.post("/videos/{video_id}/like")
def toggle_like(video_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    video = db.get(Video, video_id)
    if not video or video.status != "published": raise HTTPException(404, "Video not found")
    existing = db.scalar(select(Like).where(Like.user_id == user.id, Like.video_id == video_id))
    if existing:
        db.delete(existing); db.commit(); return {"liked": False}
    db.add(Like(user_id=user.id, video_id=video_id)); db.commit()
    return {"liked": True}

@app.post("/videos/{video_id}/comments")
def add_comment(video_id: int, data: CommentIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    video = db.get(Video, video_id)
    if not video or video.status != "published": raise HTTPException(404, "Video not found")
    comment = Comment(user_id=user.id, video_id=video_id, body=data.body)
    db.add(comment); db.commit(); db.refresh(comment)
    return {"id": comment.id, "body": comment.body, "status": comment.status}

@app.get("/videos/{video_id}/comments")
def list_comments(video_id: int, db: Session = Depends(get_db)):
    rows = db.scalars(select(Comment).where(Comment.video_id == video_id, Comment.status == "visible").order_by(Comment.created_at.desc()).limit(100))
    return [{"id": x.id, "user_id": x.user_id, "body": x.body, "created_at": x.created_at} for x in rows]

@app.post("/creators/{creator_id}/subscribe")
def subscribe(creator_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if creator_id == user.id: raise HTTPException(400, "Cannot subscribe to yourself")
    if not db.get(User, creator_id): raise HTTPException(404, "Creator not found")
    existing = db.scalar(select(Subscription).where(Subscription.follower_id == user.id, Subscription.creator_id == creator_id))
    if existing:
        db.delete(existing); db.commit(); return {"subscribed": False}
    db.add(Subscription(follower_id=user.id, creator_id=creator_id)); db.commit()
    return {"subscribed": True}

@app.get("/creator/monetization")
def monetization_status(db: Session = Depends(get_db), user: User = Depends(current_user)):
    profile = db.scalar(select(MonetizationProfile).where(MonetizationProfile.creator_id == user.id))
    return {"status": profile.status if profile else "not_eligible",
            "policy_accepted": profile.policy_accepted if profile else False,
            "reviewer_note": profile.reviewer_note if profile else None,
            "note": "Eligibility thresholds must be set in platform policy before enabling applications."}

@app.post("/admin/videos/{video_id}/review")
def review_video(video_id: int, decision: str, db: Session = Depends(get_db), admin: User = Depends(admin_user)):
    if decision not in {"published", "rejected"}: raise HTTPException(422, "Decision must be published or rejected")
    video = db.get(Video, video_id)
    if not video: raise HTTPException(404, "Video not found")
    video.status = decision; db.commit()
    return {"video_id": video_id, "status": video.status}

@app.post("/admin/creators/{creator_id}/monetization-review")
def review_monetization(creator_id: int, data: MonetizationReviewIn, db: Session = Depends(get_db), admin: User = Depends(admin_user)):
    profile = db.scalar(select(MonetizationProfile).where(MonetizationProfile.creator_id == creator_id))
    if not profile: raise HTTPException(404, "Creator profile not found")
    from datetime import datetime, timezone
    profile.status = data.status
    profile.reviewer_note = data.reviewer_note
    profile.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    return {"creator_id": creator_id, "status": profile.status}

@app.post("/admin/ad-campaigns")
def create_campaign(data: AdCampaignIn, db: Session = Depends(get_db), admin: User = Depends(admin_user)):
    campaign = AdCampaign(advertiser_name=data.advertiser_name, title=data.title, budget_inr=data.budget_inr)
    db.add(campaign); db.commit(); db.refresh(campaign)
    return {"campaign_id": campaign.id, "status": campaign.status}

@app.post("/admin/ad-events")
def record_ad_event(campaign_id: int, video_id: int, event_type: str, db: Session = Depends(get_db), admin: User = Depends(admin_user)):
    if event_type not in {"served", "impression", "completed", "invalid"}: raise HTTPException(422, "Invalid event type")
    if not db.get(AdCampaign, campaign_id) or not db.get(Video, video_id): raise HTTPException(404, "Campaign or video not found")
    # Never accept a client-provided payout amount. Settlement must validate server-side.
    event = AdEvent(campaign_id=campaign_id, video_id=video_id, event_type=event_type,
                    billable=(event_type == "impression"))
    db.add(event); db.commit()
    return {"recorded": True, "billable_candidate": event.billable, "creator_payout": 0,
            "note": "Candidate only; settlement and fraud validation are not implemented."}
