"""
Phase 7: Document Readiness Manager

Provides reusable functions for checking document readiness against scheme requirements.
"""

from typing import List, Set, Dict, Any, Optional
from models.schemas import Scheme, DocumentReadinessResponse
from services.eligibility import get_scheme_manager, SchemeManager


def get_required_documents(scheme_id: str, manager: SchemeManager) -> List[str]:
    """
    Get the list of required documents for a scheme.

    Returns empty list if scheme not found.
    """
    scheme = manager.get_scheme_by_id(scheme_id)
    if scheme is None:
        return []
    return scheme.required_documents


def normalize_document(doc: str) -> str:
    """Normalize document name for case-insensitive comparison."""
    return doc.strip().lower()


def get_available_documents_set(available_documents: List[str]) -> Set[str]:
    """
    Convert available documents list to a normalized set for efficient lookup.

    Handles duplicates and case-insensitivity.
    """
    return {normalize_document(doc) for doc in available_documents if doc}


def get_missing_documents(required_documents: List[str], available_documents: List[str]) -> List[str]:
    """
    Identify which required documents are missing from the user's available documents.

    Returns list of missing document names (in original case from required_documents).
    """
    available_set = get_available_documents_set(available_documents)

    missing = []
    for required in required_documents:
        if normalize_document(required) not in available_set:
            missing.append(required)

    return missing


def get_completed_documents(required_documents: List[str], available_documents: List[str]) -> List[str]:
    """
    Identify which required documents the user already has.

    Returns list of completed document names (in original case from required_documents).
    """
    available_set = get_available_documents_set(available_documents)

    completed = []
    for required in required_documents:
        if normalize_document(required) in available_set:
            completed.append(required)

    return completed


def calculate_readiness_percentage(required_documents: List[str], available_documents: List[str]) -> float:
    """
    Calculate document readiness percentage.

    Formula: (completed_required_documents / total_required_documents) * 100

    Returns 100.0 if no documents are required.
    """
    total = len(required_documents)
    if total == 0:
        return 100.0

    completed = get_completed_documents(required_documents, available_documents)
    percentage = (len(completed) / total) * 100
    return round(percentage, 1)


def check_document_readiness(
    scheme_id: str,
    available_documents: List[str],
    manager: SchemeManager
) -> DocumentReadinessResponse:
    """
    Check document readiness for a specific scheme.

    Returns a complete DocumentReadinessResponse.
    """
    scheme = manager.get_scheme_by_id(scheme_id)

    if scheme is None:
        # Return error response - will be handled by caller
        return DocumentReadinessResponse(
            success=False,
            scheme_id=scheme_id,
            scheme_name="Unknown",
            required_documents=[],
            documents_held=available_documents,
            missing_documents=[],
            readiness_percentage=0.0,
            message=f"Scheme with ID '{scheme_id}' not found."
        )

    required = scheme.required_documents
    missing = get_missing_documents(required, available_documents)
    completed = get_completed_documents(required, available_documents)
    readiness_pct = calculate_readiness_percentage(required, available_documents)

    # Generate message
    if total := len(required):
        completed_count = len(completed)
        if completed_count == total:
            message = f"All {total} required documents are prepared."
        elif completed_count > 0:
            message = f"{completed_count} of {total} required documents are prepared."
        else:
            message = f"None of the {total} required documents are prepared. Please prepare the required documents."
    else:
        message = "No documents are required for this scheme."

    return DocumentReadinessResponse(
        success=True,
        scheme_id=scheme.scheme_id,
        scheme_name=scheme.scheme_name,
        required_documents=required,
        documents_held=available_documents,
        missing_documents=missing,
        readiness_percentage=readiness_pct,
        message=message
    )


def calculate_overall_readiness(
    profile_documents: List[str],
    schemes: List[Scheme]
) -> Dict[str, Any]:
    """
    Calculate overall document readiness across all schemes.

    Useful for dashboard summaries.
    """
    total_schemes = len(schemes)
    if total_schemes == 0:
        return {
            "average_readiness": 0.0,
            "fully_prepared_schemes": 0,
            "total_schemes": 0
        }

    total_readiness = 0.0
    fully_prepared = 0

    for scheme in schemes:
        readiness = calculate_readiness_percentage(scheme.required_documents, profile_documents)
        total_readiness += readiness
        if readiness >= 100.0:
            fully_prepared += 1

    return {
        "average_readiness": round(total_readiness / total_schemes, 1),
        "fully_prepared_schemes": fully_prepared,
        "total_schemes": total_schemes
    }