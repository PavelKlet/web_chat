from fastapi import (
    APIRouter,
    Request,
    Depends,
    Form,
    UploadFile,
    File,
    HTTPException,
    Response,
)
from sqlalchemy.exc import DBAPIError

from .auth import auth_manager
from .models import User
from .crud import (
    RepositoryUser,
    session_dependency
)
from infrastructure.task_manager.tasks import send_registration_email
from core.config import templates
from .schemas import FriendData, UserProfileData, UserCreate

router = APIRouter()


@router.get("/register/")
async def get_index(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login/")
async def get_index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/protect/profile/")
async def protect_profile(
        user: User = Depends(auth_manager.get_user),
        session: RepositoryUser = Depends(session_dependency.get_session)
):

    user_profile = await session.get_user_profile(user.id)
    return {
        "first_name": user_profile.first_name,
        "last_name": user_profile.last_name,
        "avatar": user_profile.avatar,
        "user_id": user_profile.user_id,
        "username": user.username
    }


@router.get("/profile/")
async def get_profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/update-profile/", response_model=None)
async def get_update_profile(request: Request):
    return templates.TemplateResponse("update-profile.html",
                                      {"request": request})


@router.post("/update-profile/")
async def update_profile(
    first_name: str = Form(None),
    last_name: str = Form(None),
    avatar: UploadFile = File(None),
    user: User = Depends(auth_manager.get_user),
    session: RepositoryUser = Depends(session_dependency.get_session)
):
    try:
        await session.update_user_profile(user.id, first_name, last_name, avatar)
    except DBAPIError:
        raise HTTPException(status_code=400)


@router.get("/get/user-profile/{user_id}/")
async def get_profile_user(
        user_id: int,
        session: RepositoryUser = Depends(session_dependency.get_session)
):

    user_profile = await session.get_user_profile(user_id)
    user = await session.get_user_by_id(user_id)
    if user_profile:
        profile_data = UserProfileData(
            username=user.username,
            first_name=user_profile.first_name,
            last_name=user_profile.last_name,
            avatar=user_profile.avatar
        )
        return profile_data
    else:
        raise HTTPException(status_code=404)


@router.get("/user-profile/{user_id}/")
async def profile_user(user_id: int, request: Request):
    return templates.TemplateResponse(
        "user-profile.html",
        {"request": request}
    )


@router.post("/add/friend/{user_id}/{friend_id}/")
async def add_friend(friend_id: int,
                     user: User = Depends(auth_manager.get_user),
                     session: RepositoryUser = Depends(
                         session_dependency.get_session)
                     ):
    await session.add_user_friend(friend_id, user)
    return Response("ok")


@router.get("/friends/")
async def get_friends(page: int = 1,
                      limit: int = 10,
                      user: User = Depends(auth_manager.get_user),
                      pagination: bool = False,
                      session: RepositoryUser = Depends(
                          session_dependency.get_session)
                      ):
    friends = await session.user_friends(user, page, limit, pagination)
    friends_data = [
        FriendData(
            id=friend.id,
            avatar=friend.profile.avatar,
            username=friend.username,
            first_name=friend.profile.first_name,
            last_name=friend.profile.last_name
        ) for friend in friends
    ]
    return friends_data


@router.get("/friends/count/")
async def get_friends_count(
        user: User = Depends(auth_manager.get_user),
        session: RepositoryUser = Depends(session_dependency.get_session)
):
    friends_count = await session.get_user_friends_count(user)
    return {"friends_count": friends_count}


@router.get("/user/friends/")
async def get_user_friends(request: Request):
    return templates.TemplateResponse(
        "user-friends.html",
        {"request": request}
    )


@router.get("/not-found/")
async def get_not_found(request: Request):
    return templates.TemplateResponse("404.html", {"request": request})


@router.post("/auth/register")
async def register_user(
        user: UserCreate,
        session: RepositoryUser = Depends(session_dependency.get_session)
):
    hashed_password = auth_manager.get_password_hash(user.password)
    await session.user_register(user.email, hashed_password, user.username)
    send_registration_email.delay(user.email)

    return {"message": "User registered successfully"}


@router.post("/auth/jwt/login/")
async def login_user(
        email: str = Form(...),
        password: str = Form(...),
        session: RepositoryUser = Depends(session_dependency.get_session)
):
    user = await session.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not auth_manager.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    access_token = auth_manager.create_access_token(
        data={"sub": user.email})

    response = Response()
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return response


@router.post("/auth/jwt/logout/")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.get("/search/")
async def search_users(
        query: str,
        session: RepositoryUser = Depends(session_dependency.get_session)
):
    friends = await session.find_users_by_username(query)
    friends_data = [
        FriendData(
            id=friend.id,
            avatar=friend.profile.avatar,
            username=friend.username,
            first_name=friend.profile.first_name,
            last_name=friend.profile.last_name
        ) for friend in friends
    ]
    return friends_data


@router.get("/friends/is-friend/{other_user_id}")
async def check_friendship(
    other_user_id: int,
    current_user: User = Depends(auth_manager.get_user),
    session: RepositoryUser = Depends(session_dependency.get_session)
):
    result = await session.check_user_in_friend(current_user.id, other_user_id)
    return {"is_friend": result}

