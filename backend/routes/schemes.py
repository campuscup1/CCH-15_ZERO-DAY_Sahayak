"""
Schemes Routes - API endpoints for scheme listing and details.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, Depends
from models.schemas import Scheme, MatchResponse
from services.eligibility import get_scheme_manager

router = APIRouter(prefix="/schemes", tags=["Schemes"])

# Dependency to get scheme manager
def get_manager():
    return get_scheme_manager()


@router.get(
    "",
    response_model=dict,
    summary="List all schemes with optional filters",
    description="Returns all government schemes. Supports filtering by category, government_level, state, and search text."
)
async def list_schemes(
    category: Optional[str] = Query(None, description="Filter by scheme category"),
    government_level: Optional[str] = Query(None, description="Filter by government level (Central/State)"),
    state: Optional[str] = Query(None, description="Filter by state"),
    search: Optional[str] = Query(None, description="Search in scheme name or description"),
    manager = Depends(get_manager)
):
    """
    List all schemes with optional filters.

    Filters:
    - category: Education, Agriculture, Employment, etc.
    - government_level: Central, State
    - state: Maharashtra, All, etc.
    - search: text search in name/description
    """
    try:
        schemes = manager.load_schemes()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load schemes: {str(e)}")

    # Apply filters
    filtered = schemes

    if category:
        filtered = [s for s in filtered if s.category.lower() == category.lower()]

    if government_level:
        filtered = [s for s in filtered if s.government_level.lower() == government_level.lower()]

    if state:
        filtered = [s for s in filtered if s.state.lower() == state.lower()]

    if search:
        search_lower = search.lower()
        filtered = [
            s for s in filtered
            if search_lower in s.scheme_name.lower() or search_lower in s.description.lower()
        ]

    return {
        "success": True,
        "total_schemes": len(filtered),
        "results": [
            {
                "scheme_id": s.scheme_id,
                "scheme_name": s.scheme_name,
                "description": s.description,
                "category": s.category,
                "government_level": s.government_level,
                "state": s.state,
                "benefits": s.benefits,
                "official_website": s.official_website,
                "source_url": s.source_url,
                "last_verified_date": s.last_verified_date
            }
            for s in filtered
        ]
    }


@router.get(
    "/{scheme_id}",
    response_model=dict,
    summary="Get scheme details by ID",
    description="Returns complete details of a specific scheme including eligibility rules, required documents, and application process."
)
async def get_scheme(
    scheme_id: str,
    manager = Depends(get_manager)
):
    """Get complete details of a scheme by its ID."""
    scheme = manager.get_scheme_by_id(scheme_id)

    if scheme is None:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "NOT_FOUND",
                "message": f"Scheme with ID '{scheme_id}' not found."
            }
        )

    return {
        "success": True,
        "scheme": {
            "scheme_id": scheme.scheme_id,
            "scheme_name": scheme.scheme_name,
            "description": scheme.description,
            "category": scheme.category,
            "government_level": scheme.government_level,
            "state": scheme.state,
            "benefits": scheme.benefits,
            "eligibility_rules": scheme.eligibility_rules,
            "required_documents": scheme.required_documents,
            "application_process": scheme.application_process,
            "official_website": scheme.official_website,
            "source_url": scheme.source_url,
            "last_verified_date": scheme.last_verified_date
        }
    }