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

from infrastructure.auth.auth_manager import get_auth_manager, get_current_user, \
    AuthManager
from api.dependencies import UserServiceDep
from infrastructure.models.users import User
from infrastructure.task_manager.tasks import send_registration_email
from infrastructure.config import templates
from users.schemas import FriendData, UserProfileData, UserCreate
from infrastructure.utils.other import filter_none_values

router = APIRouter()


@router.get("/register/")
async def get_index(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login/")
async def get_index(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/protect/profile/")
async def protect_profile(
    user_service: UserServiceDep,
    user: User = Depends(get_current_user)
):
    user_profile = await user_service.get_user_profile(user.id)

    if not user_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

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
    user_service: UserServiceDep,
    first_name: str = Form(None),
    last_name: str = Form(None),
    avatar: UploadFile = File(None),
    user: User = Depends(get_current_user)

):

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    update_data = {
        "first_name": first_name,
        "last_name": last_name,
        "avatar": avatar
    }

    try:
        await user_service.update_user_profile(
            user.id,
            filter_none_values(update_data)
        )
        print(filter_none_values(update_data))
        return {"message": "Profile updated successfully"}
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to update profile {e}")


@router.get("/get/user-profile/{user_id}/")
async def get_profile_user(
        user_id: int,
        user_service: UserServiceDep,
):
    user_profile = await user_service.get_user_profile(user_id)
    if not user_profile:
        raise HTTPException(status_code=404,
                            detail="User profile not found")

    user_data = await user_service.get_user_by_id(user_id)
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    profile_data = UserProfileData(
        username=user_data.username,
        first_name=user_profile.first_name,
        last_name=user_profile.last_name,
        avatar=user_profile.avatar
    )

    return profile_data


@router.get("/user-profile/{user_id}/")
async def profile_user(user_id: int, request: Request):
    return templates.TemplateResponse(
        "user-profile.html",
        {"request": request}
    )


@router.post("/add/friend/{friend_id}/")
async def add_friend(
    friend_id: int,
    user_service: UserServiceDep,
    user: User = Depends(get_current_user),
):
    await user_service.add_user_friend(friend_id, user.id)
    return Response("ok")


@router.get("/friends/")
async def get_friends(
        user_service: UserServiceDep,
        page: int = 1,
        limit: int = 10,
        user: User = Depends(get_current_user),
        pagination: bool = False,
):
    friends = await user_service.get_user_friends(user.id, page, limit,
                                                  pagination)

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
    user_service: UserServiceDep,
    user: User = Depends(get_current_user),
):
    friends_count = await user_service.get_user_friends_count(user.id)
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
        user_service: UserServiceDep,
        authorization_manager: AuthManager = Depends(get_auth_manager)
):
    hashed_password = authorization_manager.get_password_hash(user.password)
    await user_service.register_user({
        "email": user.email,
        "hashed_password": hashed_password,
        "username": user.username
    })
    send_registration_email.delay(user.email)

    return {"message": "User registered successfully"}


@router.post("/auth/jwt/login/")
async def login_user(
        user_service: UserServiceDep,
        email: str = Form(...),
        password: str = Form(...),
        authorization_manager: AuthManager = Depends(get_auth_manager)
):
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not authorization_manager.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    access_token = authorization_manager.create_access_token(
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
    user_service: UserServiceDep,
    current_user: User = Depends(get_current_user),
):
    friends = await user_service.find_users_by_username(query)
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
        request: Request,
        other_user_id: int,
        user_service: UserServiceDep,
        authorization_manager: AuthManager = Depends(get_auth_manager)
):
    user = await authorization_manager.get_user(request=request)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await user_service.check_user_in_friend(user.id, other_user_id)

    return {"is_friend": result}
