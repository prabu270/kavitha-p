import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from sqlalchemy import select

from sqlalchemy.orm import Session

from ..config import get_settings

from ..database import get_db

from ..dependencies import (
    get_current_user,
)

from ..models import (
    RecommendationHistory,
    User,
)

from ..schemas import (
    HomeRequest,
    PartyRequest,
)

from ..services.gemini_service import (
    generate,
)


router = APIRouter(
    tags=["Recommendations"]
)


def save_history(
    db: Session,
    user: User,
    planner: str,
    budget: int,
    request_data: dict,
    result: dict,
):

    history = RecommendationHistory(
        user_id=user.id,

        planner=planner,

        budget=budget,

        request_json=json.dumps(
            request_data,
            default=str,
        ),

        result_json=json.dumps(
            result,
            default=str,
        ),
    )

    db.add(history)

    db.commit()

    return history


@router.post(
    "/generate-home"
)
async def generate_home(
    data: HomeRequest,
    user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    payload = data.model_dump()

    result = await generate(
        "home",
        payload,
    )

    save_history(
        db=db,
        user=user,
        planner="home",
        budget=data.budget,
        request_data=payload,
        result=result,
    )

    return result


@router.post(
    "/generate-party"
)
async def generate_party(
    data: PartyRequest,
    user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    payload = data.model_dump()

    result = await generate(
        "party",
        payload,
    )

    save_history(
        db=db,
        user=user,
        planner="party",
        budget=data.budget,
        request_data=payload,
        result=result,
    )

    return result


@router.post(
    "/generate-jewelry"
)
async def generate_jewelry(
    budget: int = Form(...),

    occasion: str = Form(...),

    style: str = Form(
        "Elegant"
    ),

    outfit_color: str = Form(
        "Not specified"
    ),

    metal_preference: str = Form(
        "Any"
    ),

    outfit_image: UploadFile | None = File(
        None
    ),

    user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):

    if budget <= 0:

        raise HTTPException(
            status_code=422,
            detail="Budget must be greater than zero",
        )

    if not occasion.strip():

        raise HTTPException(
            status_code=422,
            detail="Occasion is required",
        )

    settings = get_settings()

    image_bytes = None

    image_mime = None

    if outfit_image:

        if (
            outfit_image.content_type
            not in settings.allowed_image_type_set
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "Only JPEG, PNG and WebP "
                    "images are supported"
                ),
            )

        image_bytes = (
            await outfit_image.read()
        )

        max_size = (
            settings.max_upload_mb
            * 1024
            * 1024
        )

        if len(image_bytes) > max_size:

            raise HTTPException(
                status_code=413,
                detail="Image is too large",
            )

        image_mime = (
            outfit_image.content_type
        )

    payload = {
        "budget": budget,

        "occasion": occasion.strip(),

        "style": style.strip(),

        "outfit_color": outfit_color.strip(),

        "metal_preference": (
            metal_preference.strip()
        ),

        "image_attached": bool(
            image_bytes
        ),
    }

    result = await generate(
        "jewelry",
        payload,
        image_bytes,
        image_mime,
    )

    save_history(
        db=db,
        user=user,
        planner="jewelry",
        budget=budget,
        request_data=payload,
        result=result,
    )

    return result


@router.get(
    "/recommendations-details/{history_id}"
)
def recommendation_details(
    history_id: int,

    user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):

    record = db.scalar(
        select(
            RecommendationHistory
        ).where(
            RecommendationHistory.id
            == history_id,

            RecommendationHistory.user_id
            == user.id,
        )
    )

    if not record:

        raise HTTPException(
            status_code=404,
            detail="Recommendation not found",
        )

    return {
        "id": record.id,

        "planner": record.planner,

        "request": json.loads(
            record.request_json
        ),

        "result": json.loads(
            record.result_json
        ),

        "created_at": record.created_at,
    }


@router.get("/history")
def history(
    user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db),
):

    records = db.scalars(
        select(
            RecommendationHistory
        )
        .where(
            RecommendationHistory.user_id
            == user.id
        )
        .order_by(
            RecommendationHistory.created_at.desc()
        )
        .limit(50)
    ).all()

    result = []

    for record in records:

        data = json.loads(
            record.result_json
        )

        result.append(
            {
                "id": record.id,

                "planner": record.planner,

                "budget": record.budget,

                "created_at": record.created_at,

                "summary": data.get(
                    "summary",
                    "",
                ),
            }
        )

    return result