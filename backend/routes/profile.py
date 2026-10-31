"""
Profile Routes - API endpoints for profile validation and storage.
"""

from fastapi import APIRouter, HTTPException
from models.schemas import UserProfile
from typing import Optional

router = APIRouter(prefix="/profile", tags=["Profile"])

# In-memory storage for demo (in production, would use database)
_stored_profile: Optional[UserProfile] = None


@router.post(
    "",
    response_model=dict,
    summary="Validate and store user profile",
    description="Accepts a user profile, validates it using Pydantic models, and stores it for matching."
)
async def create_profile(profile: UserProfile):
    """
    Validate and accept user profile.

    The profile is stored in-memory for the matching endpoint to use.
    All fields are optional, but providing more information yields better matching results.
    """
    global _stored_profile

    try:
        _stored_profile = profile

        return {
            "success": True,
            "message": "Profile validated and stored successfully.",
            "profile": profile.model_dump(mode='json')
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": f"Profile validation failed: {str(e)}"
            }
        )


@router.get(
    "",
    response_model=dict,
    summary="Get stored profile",
    description="Returns the currently stored user profile if any."
)
async def get_profile():
    """Get the currently stored user profile."""
    global _stored_profile

    if _stored_profile is None:
        return {
            "success": True,
            "message": "No profile stored yet.",
            "profile": None
        }

    return {
        "success": True,
        "profile": _stored_profile.model_dump(mode='json')
    }


@router.delete(
    "",
    response_model=dict,
    summary="Clear stored profile",
    description="Clears the currently stored user profile."
)
async def clear_profile():
    """Clear the stored user profile."""
    global _stored_profile
    _stored_profile = None

    return {
        "success": True,
        "message": "Profile cleared successfully."
    }