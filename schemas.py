from pydantic import BaseModel, EmailStr, Field, ConfigDict

class RegisterIn(BaseModel):
    email: EmailStr
    display_name: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=12, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    display_name: str
    model_config = ConfigDict(from_attributes=True)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class VideoOut(BaseModel):
    id: int
    creator_id: int
    title: str
    description: str
    duration_seconds: int
    is_short: bool
    status: str
    model_config = ConfigDict(from_attributes=True)

class CommentIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)

class MonetizationReviewIn(BaseModel):
    status: str = Field(pattern="^(eligible|rejected|under_review)$")
    reviewer_note: str = Field(default="", max_length=2000)

class AdCampaignIn(BaseModel):
    advertiser_name: str = Field(min_length=2, max_length=120)
    title: str = Field(min_length=2, max_length=150)
    budget_inr: float = Field(gt=0)
