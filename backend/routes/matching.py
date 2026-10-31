"""
Matching Routes - API endpoints for eligibility matching.
"""

from fastapi import APIRouter, HTTPException, Depends
from models.schemas import UserProfile, MatchResponse
from services.eligibility import evaluate_all_schemes, get_scheme_manager, SchemeManager

router = APIRouter(prefix="/match", tags=["Matching"])


def get_manager() -> SchemeManager:
    return get_scheme_manager()


@router.post(
    "",
    response_model=MatchResponse,
    summary="Evaluate profile against all schemes",
    description="Takes a user profile and evaluates it against all government schemes using the eligibility engine. Returns match status, condition explanations, and document readiness for each scheme."
)
async def match_profile(profile: UserProfile, manager: SchemeManager = Depends(get_manager)):
    """
    Evaluate user profile against all schemes.

    Returns:
    - MATCH: All mandatory conditions satisfied
    - POTENTIAL_MATCH: Some required information missing
    - NOT_MATCH: At least one mandatory condition failed

    Includes condition-level explanations and document readiness for each scheme.
    """
    try:
        schemes = manager.load_schemes()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load schemes: {str(e)}")

    if not schemes:
        raise HTTPException(
            status_code=500,
            detail="No schemes available for matching."
        )

    try:
        result = evaluate_all_schemes(profile, schemes)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Matching evaluation failed: {str(e)}"
        )


@router.post(
    "/stored",
    response_model=MatchResponse,
    summary="Evaluate stored profile against all schemes",
    description="Uses the currently stored profile (from POST /profile) to evaluate against all schemes."
)
async def match_stored_profile(manager: SchemeManager = Depends(get_manager)):
    """Evaluate the stored profile against all schemes."""
    # This would need access to the stored profile from profile routes
    # For now, we'll just document this endpoint
    raise HTTPException(
        status_code=501,
        detail="This endpoint requires integration with profile storage. Use POST /match with explicit profile instead."
    )