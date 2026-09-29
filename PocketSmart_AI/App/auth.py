from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)

from sqlalchemy import func, select

from sqlalchemy.orm import Session

from ..auth import (
    create_access_token,
    hash_password,
    verify_password,
)

from ..database import get_db

from ..dependencies import (
    get_current_user,
)

from ..models import (
    RecommendationHistory,
    User,
)

from ..schemas import (
    Token,
    UserLogin,
    UserOut,
    UserRegister,
)


router = APIRouter(
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
)
def register(
    data: UserRegister,
    db: Session = Depends(get_db),
):

    email = (
        data.email
        .strip()
        .lower()
    )

    existing_user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if existing_user:

        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user = User(
        email=email,
        full_name=data.full_name.strip(),
        password_hash=hash_password(
            data.password
        ),
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=Token,
)
def login(
    data: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
):

    email = (
        data.email
        .strip()
        .lower()
    )

    user = db.scalar(
        select(User).where(
            User.email == email
        )
    )

    if (
        not user
        or not verify_password(
            data.password,
            user.password_hash,
        )
    ):

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(
        str(user.id)
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=7200,
    )

    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(
    response: Response,
):

    response.delete_cookie(
        "access_token"
    )

    return {
        "message": "Logged out successfully"
    }


@router.get(
    "/token",
    response_model=Token,
)
def token(
    request: Request,
    user: User = Depends(
        get_current_user
    ),
):

    token_value = request.cookies.get(
        "access_token"
    )

    if not token_value:

        raise HTTPException(
            status_code=401,
            detail="Token not available",
        )

    return {
        "access_token": token_value,
        "token_type": "bearer",
    }


@router.get("/session-info")
def session_info(
    user: User = Depends(
        get_current_user
    ),
):

    return {
        "logged_in": True,
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
    }


@router.get("/session-data")
def session_data(
    user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):

    count = db.scalar(
        select(
            func.count(
                RecommendationHistory.id
            )
        ).where(
            RecommendationHistory.user_id
            == user.id
        )
    )

    return {
        "user": UserOut.model_validate(user),
        "recommendation_count": count or 0,
    }
