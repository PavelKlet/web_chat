from typing import List, Optional

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

from app.application.services.auth.auth_manager import get_auth_manager, get_current_user, \
    AuthManager
from app.api.dependencies import UserServiceDep
from app.infrastructure.models.relational.users import User
from app.infrastructure.config.config import templates
from .schemas.users import UserCreate, FriendSchema, UserRead, ProfileSchema
from app.infrastructure.utils.other import filter_none_values
from ..application.exceptions import EmailAlreadyExistsException, UsernameAlreadyExistsException

router = APIRouter()


@router.get("/register/")
async def get_index(request: Request):
    """Renders the registration page for new users."""

    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/login/")
async def get_index(request: Request):
    """Renders the login page for existing users."""

    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/protect/profile/", response_model=UserRead)
async def protect_profile(
    user: UserRead = Depends(get_current_user)
):
    """Retrieves the protected profile data for the authenticated user."""
    return user

@router.get("/profile/")
async def get_profile(request: Request):
    """Renders the user's profile page."""

    return templates.TemplateResponse("profile.html", {"request": request})


@router.get("/update-profile/", response_model=None)
async def get_update_profile(request: Request):
    """Renders the page for updating the user's profile."""
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
    """Updates the user's profile with new details."""

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
        return {"message": "Profile updated successfully"}
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to update profile {e}")


@router.get("/get/user-profile/{user_id}/", response_model=UserRead)
async def get_profile_user(
        user_id: int,
        user_service: UserServiceDep,
):
    """Retrieves the profile data of a user by their ID."""
    user = await user_service.get_user_with_profile(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/user-profile/{user_id}/")
async def profile_user(user_id: int, request: Request):
    """
        Renders the user profile page for the specified user.
    """
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
    """
        Adds the specified user as a friend to the current user's friend list.
    """
    await user_service.add_user_friend(friend_id, user.id)
    return Response("ok")


@router.get("/friends/", response_model=Optional[List[FriendSchema]])
async def get_friends(
        user_service: UserServiceDep,
        page: int = 1,
        limit: int = 10,
        user: User = Depends(get_current_user),
        pagination: bool = False,
):
    """
        Retrieves a paginated list of friends for the current user.
    """
    friends = await user_service.get_user_friends(user.id, page, limit,
                                                  pagination)
    return friends


@router.get("/user/friends/")
async def get_user_friends(request: Request):
    """
        Renders the friends list page for the current user.
    """
    return templates.TemplateResponse(
        "user-friends.html",
        {"request": request}
    )


@router.get("/not-found/")
async def get_not_found(request: Request):
    """
        Renders the 404 error page.
    """
    return templates.TemplateResponse("404.html", {"request": request})


@router.post("/auth/register")
async def register_user(
        user: UserCreate,
        user_service: UserServiceDep,
        authorization_manager: AuthManager = Depends(get_auth_manager)
):
    """
        Registers a new user with the provided details.
    """

    hashed_password = authorization_manager.get_password_hash(user.password)
    try:
        await user_service.register_user({
            "email": user.email,
            "hashed_password": hashed_password,
            "username": user.username
        })
    except (EmailAlreadyExistsException, UsernameAlreadyExistsException) as e:
        raise HTTPException(status_code=400, detail=str(e))


    return {"message": "User registered successfully"}


@router.post("/auth/jwt/login/")
async def login_user(
        user_service: UserServiceDep,
        email: str = Form(...),
        password: str = Form(...),
        authorization_manager: AuthManager = Depends(get_auth_manager)
):
    """
       Logs in a user by verifying their credentials and generates a JWT token.
    """
    user = await user_service.get_user_by_email_private(email)

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
    """
        Logs out the current user by removing the access token.
    """
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


@router.get("/search/", response_model=Optional[List[FriendSchema]])
async def search_users(
    user_service: UserServiceDep,
    query: str,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
):
    """
        Searches for users based on the provided query string.
    """

    users = await user_service.find_users_by_username(query, page, limit)
    return users


@router.get("/friends/is-friend/{other_user_id}")
async def check_friendship(
        request: Request,
        other_user_id: int,
        user_service: UserServiceDep,
        authorization_manager: AuthManager = Depends(get_auth_manager)
):
    """
        Checks if the specified user is a friend of the current user.
    """

    user = await authorization_manager.get_user(request=request)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    result = await user_service.check_user_in_friend(user.id, other_user_id)

    return {"is_friend": result}
