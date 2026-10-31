"""
Comparison Routes - API endpoints for scheme comparison.
"""

from fastapi import APIRouter, HTTPException, Depends
from models.schemas import SchemeComparisonRequest, SchemeComparisonResponse, SchemeComparisonItem
from services.eligibility import get_scheme_manager, SchemeManager

router = APIRouter(prefix="/compare", tags=["Comparison"])


def get_manager() -> SchemeManager:
    return get_scheme_manager()


def validate_comparison_request(
    request: SchemeComparisonRequest
) -> List[str]:
    """Validate comparison request parameters."""
    errors = []

    if not request.scheme_ids:
        errors.append("scheme_ids cannot be empty")
        return errors

    if len(request.scheme_ids) < 2:
        errors.append("At least 2 scheme IDs are required for comparison")

    if len(request.scheme_ids) > 5:
        errors.append("Maximum 5 scheme IDs allowed for comparison")

    # Check for duplicates
    if len(request.scheme_ids) != len(set(request.scheme_ids)):
        errors.append("Duplicate scheme IDs are not allowed")

    return errors


def get_scheme_comparison_item(scheme) -> SchemeComparisonItem:
    """
    Convert a Scheme model to a SchemeComparisonItem.

    Builds a concise comparison representation.
    """
    # Build eligibility summary
    rules_summary_parts = []
    if "min_age" in scheme.eligibility_rules and scheme.eligibility_rules["min_age"] is not None:
        rules_summary_parts.append(f"Age >= {scheme.eligibility_rules['min_age']}")

    if "max_age" in scheme.eligibility_rules and scheme.eligibility_rules["max_age"] is not None:
        rules_summary_parts.append(f"Age <= {scheme.eligibility_rules['max_age']}")

    if "max_income" in scheme.eligibility_rules and scheme.eligibility_rules["max_income"] is not None:
        rules_summary_parts.append(f"Income <= {scheme.eligibility_rules['max_income']}")

    if "domicile" in scheme.eligibility_rules and scheme.eligibility_rules["domicile"] != "All":
        rules_summary_parts.append(f"Domicile: {scheme.eligibility_rules['domicile']}")

    if "category" in scheme.eligibility_rules:
        cats = scheme.eligibility_rules["category"]
        if isinstance(cats, str):
            rules_summary_parts.append(f"Category: {cats}")
        elif isinstance(cats, list) and cats:
            rules_summary_parts.append(f"Category: {', '.join(cats)}")

    if "education_level" in scheme.eligibility_rules:
        edu = scheme.eligibility_rules["education_level"]
        if isinstance(edu, str):
            rules_summary_parts.append(f"Education: {edu}")
        elif isinstance(edu, list) and edu:
            rules_summary_parts.append(f"Education: {', '.join(edu)}")

    if "occupation" in scheme.eligibility_rules:
        occ = scheme.eligibility_rules["occupation"]
        if isinstance(occ, str):
            rules_summary_parts.append(f"Occupation: {occ}")
        elif isinstance(occ, list) and occ:
            rules_summary_parts.append(f"Occupation: {', '.join(occ)}")

    eligibility_summary = "; ".join(rules_summary_parts) if rules_summary_parts else "No specific eligibility criteria"

    return SchemeComparisonItem(
        scheme_id=scheme.scheme_id,
        scheme_name=scheme.scheme_name,
        category=scheme.category,
        government_level=scheme.government_level,
        state=scheme.state,
        benefits=scheme.benefits,
        eligibility_summary=eligibility_summary,
        required_documents=scheme.required_documents,
        application_process=scheme.application_process,
        official_website=scheme.official_website
    )


@router.post(
    "",
    response_model=SchemeComparisonResponse,
    summary="Compare multiple schemes",
    description="Compare two to five schemes side by side including key details, eligibility criteria, benefits, and requirements."
)
async def compare_schemes(
    request: SchemeComparisonRequest,
    manager: SchemeManager = Depends(get_manager)
):
    """
    Compare multiple schemes.

    Request body:
    {
        "scheme_ids": ["SCH001", "SCH002", "SCH003"]
    }

    Returns comparison of up to 5 schemes with details.
    """
    # Validate request
    validation_errors = validate_comparison_request(request)
    if validation_errors:
        error_message = "; ".join(validation_errors)
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error": "VALIDATION_ERROR",
                "message": error_message
            }
        )

    # Load schemes
    try:
        schemes = manager.load_schemes()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load schemes: {str(e)}")

    if not schemes:
        raise HTTPException(status_code=500, detail="No schemes available for comparison.")

    # Find requested schemes
    requested_ids = set(request.scheme_ids)
    scheme_map = {s.scheme_id: s for s in schemes}
    found_schemes = []

    for scheme_id in requested_ids:
        if scheme_id in scheme_map:
            found_schemes.append(scheme_map[scheme_id])
        else:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error": "NOT_FOUND",
                    "message": f"Scheme with ID '{scheme_id}' not found."
                }
            )

    if len(found_schemes) != len(requested_ids):
        found_ids = {s.scheme_id for s in found_schemes}
        missing = requested_ids - found_ids
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error": "NOT_FOUND",
                "message": f"The following scheme IDs were not found: {', '.join(missing)}"
            }
        )

    # Build comparison items
    comparison_items = [get_scheme_comparison_item(scheme) for scheme in found_schemes]

    return SchemeComparisonResponse(
        success=True,
        total_compared=len(comparison_items),
        schemes=comparison_items
    )