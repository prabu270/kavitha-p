from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):
    email: str = Field(
        min_length=5,
        max_length=255,
    )

    full_name: str = Field(
        min_length=2,
        max_length=120,
    )

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserLogin(BaseModel):
    email: str

    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    email: str

    full_name: str


class Token(BaseModel):
    access_token: str

    token_type: str = "bearer"


class HomeItem(BaseModel):
    category: str = Field(
        min_length=2,
        max_length=80,
    )

    quantity: int = Field(
        ge=1,
        le=100,
    )


class HomeRequest(BaseModel):
    budget: int = Field(
        gt=0,
        le=10_000_000,
    )

    room_type: str = Field(
        min_length=2,
        max_length=80,
    )

    style: str = Field(
        default="Modern",
        min_length=2,
        max_length=80,
    )

    items: list[HomeItem] = Field(
        min_length=1,
        max_length=30,
    )


class PartyRequest(BaseModel):
    budget: int = Field(
        gt=0,
        le=10_000_000,
    )

    guest_count: int = Field(
        gt=0,
        le=10_000,
    )

    event_type: str = Field(
        min_length=2,
        max_length=80,
    )

    venue: str = Field(
        default="Flexible",
        min_length=2,
        max_length=120,
    )

    city: str = Field(
        default="India",
        min_length=2,
        max_length=100,
    )


class JewelryRequest(BaseModel):
    budget: int = Field(
        gt=0,
        le=10_000_000,
    )

    occasion: str = Field(
        min_length=2,
        max_length=100,
    )

    style: str = Field(
        default="Elegant",
        min_length=2,
        max_length=100,
    )

    outfit_color: str = Field(
        default="Not specified",
        max_length=100,
    )

    metal_preference: str = Field(
        default="Any",
        max_length=80,
    )


class RecommendationItem(BaseModel):
    title: str

    category: str

    estimated_price: int = Field(
        ge=0
    )

    platform: str

    reason: str

    search_url: str


class RecommendationResponse(BaseModel):
    planner: Literal[
        "home",
        "party",
        "jewelry",
    ]

    budget: int

    allocation: dict[str, int]

    total_estimated: int

    summary: str

    items: list[RecommendationItem]

    ai_generated: bool = False

    note: str | None = None