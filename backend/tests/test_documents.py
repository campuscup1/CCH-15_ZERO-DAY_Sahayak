"""
Document Readiness Tests
"""

import sys
from pathlib import Path
import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app
from models.schemas import UserProfile
from services.eligibility import get_scheme_manager
from services.document_manager import (
    get_required_documents,
    get_missing_documents,
    get_completed_documents,
    calculate_readiness_percentage,
    check_document_readiness,
)

client = TestClient(app)


def test_get_documents_valid_scheme():
    """Test GET /documents/{scheme_id} for valid scheme."""
    response = client.get("/documents/SCH001")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["scheme_id"] == "SCH001"
    assert "required_documents" in data
    assert "total_required_documents" in data
    assert len(data["required_documents"]) == data["total_required_documents"]


def test_get_documents_unknown_scheme():
    """Test GET /documents/{scheme_id} for unknown scheme."""
    response = client.get("/documents/UNKNOWN999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "NOT_FOUND"


def test_check_documents_all_available():
    """Test POST /documents/check with all required documents."""
    request_data = {
        "scheme_id": "SCH001",
        "available_documents": [
            "Aadhaar Card",
            "Income Certificate",
            "Domicile Certificate",
            "Caste Certificate",
            "Previous Year Marksheet",
            "Fee Receipt"
        ]
    }

    response = client.post("/documents/check", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["readiness_percentage"] == 100.0
    assert len(data["missing_documents"]) == 0
    # The response returns documents_held, not completed_documents
    assert len(data["documents_held"]) == 6


def test_check_documents_some_missing():
    """Test POST /documents/check with some missing documents."""
    request_data = {
        "scheme_id": "SCH001",
        "available_documents": ["Aadhaar Card", "Income Certificate"]
    }

    response = client.post("/documents/check", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["readiness_percentage"] == 33.3  # 2 out of 6
    assert len(data["missing_documents"]) == 4
    assert "Domicile Certificate" in data["missing_documents"]
    assert "Caste Certificate" in data["missing_documents"]


def test_check_documents_none_available():
    """Test POST /documents/check with no documents."""
    request_data = {
        "scheme_id": "SCH001",
        "available_documents": []
    }

    response = client.post("/documents/check", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["readiness_percentage"] == 0.0
    assert len(data["missing_documents"]) == 6


def test_check_documents_empty_required_list():
    """Test document check for scheme with no required documents."""
    # We need a scheme with empty required_documents - use a test fixture or mock
    # For now, test the service function directly
    from services.document_manager import calculate_readiness_percentage
    readiness = calculate_readiness_percentage([], [])
    assert readiness == 100.0

    readiness = calculate_readiness_percentage([], ["Aadhaar Card"])
    assert readiness == 100.0


def test_check_documents_duplicate_available():
    """Test duplicate available documents are handled."""
    request_data = {
        "scheme_id": "SCH001",
        "available_documents": ["Aadhaar Card", "Aadhaar Card", "Income Certificate", "Income Certificate"]
    }

    response = client.post("/documents/check", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["readiness_percentage"] == 33.3  # 2 unique out of 6


def test_check_documents_case_insensitive():
    """Test case-insensitive document matching."""
    request_data = {
        "scheme_id": "SCH001",
        "available_documents": ["aadhaar card", "INCOME CERTIFICATE"]
    }

    response = client.post("/documents/check", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["readiness_percentage"] == 33.3  # 2 out of 6


def test_check_documents_extra_irrelevant():
    """Test extra documents not required by scheme are ignored."""
    request_data = {
        "scheme_id": "SCH001",
        "available_documents": [
            "Aadhaar Card",
            "Income Certificate",
            "Passport",  # Not required
            "Driving License"  # Not required
        ]
    }

    response = client.post("/documents/check", json=request_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["readiness_percentage"] == 33.3  # Only 2 required docs present


def test_calculate_readiness_percentage():
    """Test readiness percentage calculation."""
    required = ["Doc1", "Doc2", "Doc3", "Doc4"]

    assert calculate_readiness_percentage(required, []) == 0.0
    assert calculate_readiness_percentage(required, ["Doc1"]) == 25.0
    assert calculate_readiness_percentage(required, ["Doc1", "Doc2"]) == 50.0
    assert calculate_readiness_percentage(required, ["Doc1", "Doc2", "Doc3"]) == 75.0
    assert calculate_readiness_percentage(required, ["Doc1", "Doc2", "Doc3", "Doc4"]) == 100.0

    # Empty required
    assert calculate_readiness_percentage([], []) == 100.0
    assert calculate_readiness_percentage([], ["Doc1"]) == 100.0


def test_readiness_never_changes_eligibility():
    """Verify document readiness is separate from eligibility status."""
    # Test through the matching endpoint - document readiness should not affect match status
    profile = {
        "age": 20,
        "annual_income": 150000,
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "category": "OBC",
        "occupation": "Student"
    }

    # Get match result without documents
    response1 = client.post("/match", json=profile)
    assert response1.status_code == 200
    data1 = response1.json()

    # Get match result with all documents
    profile["documents_held"] = [
        "Aadhaar Card", "Income Certificate", "Domicile Certificate",
        "Caste Certificate", "Previous Year Marksheet", "Fee Receipt"
    ]
    response2 = client.post("/match", json=profile)
    assert response2.status_code == 200
    data2 = response2.json()

    # Eligibility status should be identical - documents don't change match status
    for i in range(12):
        assert data1["results"][i]["status"] == data2["results"][i]["status"]


def test_check_documents_missing_scheme_id():
    """Test POST /documents/check without scheme_id."""
    request_data = {
        "available_documents": ["Aadhaar Card"]
    }

    response = client.post("/documents/check", json=request_data)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "VALIDATION_ERROR"


def test_check_documents_invalid_available_docs():
    """Test POST /documents/check with invalid available_documents."""
    request_data = {
        "scheme_id": "SCH001",
        "available_documents": "not a list"
    }

    response = client.post("/documents/check", json=request_data)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "VALIDATION_ERROR"


def test_service_get_required_documents():
    """Test service function get_required_documents."""
    manager = get_scheme_manager()
    docs = get_required_documents("SCH001", manager)
    assert len(docs) == 6
    assert "Aadhaar Card" in docs


def test_service_get_missing_documents():
    """Test service function get_missing_documents."""
    required = ["Aadhaar Card", "Income Certificate", "Domicile Certificate"]
    available = ["Aadhaar Card"]

    missing = get_missing_documents(required, available)
    assert "Income Certificate" in missing
    assert "Domicile Certificate" in missing
    assert "Aadhaar Card" not in missing


def test_service_get_completed_documents():
    """Test service function get_completed_documents."""
    required = ["Aadhaar Card", "Income Certificate", "Domicile Certificate"]
    available = ["Aadhaar Card"]

    completed = get_completed_documents(required, available)
    assert "Aadhaar Card" in completed
    assert len(completed) == 1


def test_service_normalize_document():
    """Test document normalization."""
    from services.document_manager import normalize_document, get_available_documents_set

    assert normalize_document("Aadhaar Card") == "aadhaar card"
    assert normalize_document("  INCOME CERTIFICATE  ") == "income certificate"

    docs = get_available_documents_set(["Aadhaar Card", "aadhaar card", "Income Certificate"])
    assert len(docs) == 2  # Duplicates removed
    assert "aadhaar card" in docs
    assert "income certificate" in docs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])