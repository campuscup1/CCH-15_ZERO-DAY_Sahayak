"""
Document Routes - API endpoints for document readiness checking.
"""

from fastapi import APIRouter, HTTPException, Depends
from models.schemas import DocumentReadinessResponse
from services.eligibility import get_scheme_manager, SchemeManager
from services.document_manager import (
    get_required_documents,
    check_document_readiness,
    calculate_readiness_percentage,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


def get_manager() -> SchemeManager:
    return get_scheme_manager()


@router.get(
    "/{scheme_id}",
    response_model=dict,
    summary="Get required documents for a scheme",
    description="Returns the list of required documents for a specific scheme."
)
async def get_scheme_documents(
    scheme_id: str,
    manager: SchemeManager = Depends(get_manager)
):
    """Get required documents for a scheme by ID."""
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
        "scheme_id": scheme.scheme_id,
        "scheme_name": scheme.scheme_name,
        "required_documents": scheme.required_documents,
        "total_required_documents": len(scheme.required_documents)
    }


@router.post(
    "/check",
    response_model=DocumentReadinessResponse,
    summary="Check document readiness for a scheme",
    description="Checks which required documents the user has and calculates readiness percentage. This is a checklist completion metric only, not an eligibility or approval probability."
)
async def check_documents(
    request: dict,
    manager: SchemeManager = Depends(get_manager)
):
    """
    Check document readiness for a scheme.

    Request body:
    {
        "scheme_id": "SCH001",
        "available_documents": ["Aadhaar Card", "Income Certificate"]
    }

    Returns:
    - required_documents: All documents required by the scheme
    - documents_held: Documents the user provided
    - missing_documents: Required documents not yet prepared
    - readiness_percentage: Checklist completion percentage (0-100)
    - message: Human-readable summary
    """
    scheme_id = request.get("scheme_id")
    available_documents = request.get("available_documents", [])

    if not scheme_id:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "scheme_id is required."
            }
        )

    if not isinstance(available_documents, list):
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": "available_documents must be a list."
            }
        )

    result = check_document_readiness(scheme_id, available_documents, manager)

    if not result.success:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "NOT_FOUND",
                "message": result.message
            }
        )

    return result