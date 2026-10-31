"""
Gap Analysis Routes - API endpoints for eligibility gap analysis.
"""

from fastapi import APIRouter, HTTPException, Depends
from models.schemas import UserProfile, GapAnalysisResponse
from services.eligibility import get_scheme_manager, SchemeManager
from services.gap_analyzer import analyze_all_scheme_gaps

router = APIRouter(prefix="/analyze", tags=["Gap Analysis"])


def get_manager() -> SchemeManager:
    return get_scheme_manager()


@router.post(
    "",
    response_model=GapAnalysisResponse,
    summary="Analyze eligibility gaps for user profile",
    description="Evaluates the user profile against all schemes and provides detailed gap analysis including satisfied conditions, failed conditions, missing information, and recommendations."
)
async def analyze_gaps(profile: UserProfile, manager: SchemeManager = Depends(get_manager)):
    """
    Perform gap analysis on user profile against all schemes.

    Returns detailed analysis for each scheme including:
    - Eligibility status and summary
    - Satisfied conditions
    - Failed conditions
    - Missing information
    - Verification requirements
    - Recommended actions
    - Document readiness
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
            detail="No schemes available for analysis."
        )

    try:
        result = analyze_all_scheme_gaps(profile, schemes)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gap analysis failed: {str(e)}"
        )