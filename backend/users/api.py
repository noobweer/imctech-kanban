from ninja_extra import NinjaExtraAPI
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.authentication import JWTAuth
from .models import UserProfile
from .schemas import RegisterSchema, UserOutSchema, UserUpdateSchema
from typing import List


api = NinjaExtraAPI()

# JWT token endpoints
api.register_controllers(NinjaJWTDefaultController)


def user_to_schema(user: User) -> UserOutSchema:
    """Convert User + UserProfile to UserOutSchema"""
    profile = user.profile
    return UserOutSchema(
        username=user.username,
        name=profile.name,
        role=profile.role,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@api.post("/auth/register", response=UserOutSchema, tags=["auth"])
def register(request, data: RegisterSchema):
    """Register new user with profile"""
    if User.objects.filter(username=data.username).exists():
        return api.create_response(
            request,
            {"detail": "Username already exists"},
            status=400,
        )

    # Create user with hashed password
    user = User.objects.create_user(
        username=data.username,
        password=data.password,
    )

    # Create profile
    profile = UserProfile.objects.create(
        user=user,
        name=data.name,
        role=data.role,
    )

    return user_to_schema(user)


@api.get("/auth/me", response=UserOutSchema, auth=JWTAuth(), tags=["auth"])
def get_current_user(request):
    """Get current authenticated user"""
    return user_to_schema(request.auth)


@api.get("/users", response=List[UserOutSchema], auth=JWTAuth(), tags=["users"])
def list_users(request):
    """List all users"""
    users = User.objects.select_related('profile').all()
    return [user_to_schema(user) for user in users]


@api.get("/users/{username}", response=UserOutSchema, auth=JWTAuth(), tags=["users"])
def get_user(request, username: str):
    """Get user by username"""
    user = get_object_or_404(User.objects.select_related('profile'), username=username)
    return user_to_schema(user)


@api.patch("/users/{username}", response=UserOutSchema, auth=JWTAuth(), tags=["users"])
def update_user(request, username: str, data: UserUpdateSchema):
    """Update user (self or staff only)"""
    user = get_object_or_404(User.objects.select_related('profile'), username=username)

    # Permission check: user can update self, or staff can update anyone
    if request.auth.username != username and not request.auth.is_staff:
        return api.create_response(
            request,
            {"detail": "Permission denied"},
            status=403,
        )

    # Update profile fields
    profile = user.profile
    if data.name is not None:
        profile.name = data.name
    if data.role is not None:
        profile.role = data.role
    profile.save()

    # Update password if provided
    if data.password is not None:
        user.set_password(data.password)
        user.save()

    return user_to_schema(user)


@api.delete("/users/{username}", auth=JWTAuth(), tags=["users"])
def delete_user(request, username: str):
    """Delete user (self or staff only)"""
    user = get_object_or_404(User, username=username)

    # Permission check: user can delete self, or staff can delete anyone
    if request.auth.username != username and not request.auth.is_staff:
        return api.create_response(
            request,
            {"detail": "Permission denied"},
            status=403,
        )

    user.delete()
    return {"success": True}
