"""
Scheme Comparison Tests
"""

import sys
from pathlib import Path
import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app
from services.eligibility import get_scheme_manager

client = TestClient(app)


def test_compare_two_schemes():
    """Test comparing two valid schemes."""
    request_data = {"scheme_ids": ["SCH001", "SCH002"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_compared"] == 2
    assert len(data["schemes"]) == 2

    scheme_ids = {s["scheme_id"] for s in data["schemes"]}
    assert scheme_ids == {"SCH001", "SCH002"}

    # Verify all comparison fields present
    for scheme in data["schemes"]:
        assert "scheme_id" in scheme
        assert "scheme_name" in scheme
        assert "category" in scheme
        assert "government_level" in scheme
        assert "state" in scheme
        assert "benefits" in scheme
        assert "eligibility_summary" in scheme
        assert "required_documents" in scheme
        assert "application_process" in scheme
        assert "official_website" in scheme


def test_compare_five_schemes():
    """Test comparing five valid schemes (maximum)."""
    request_data = {"scheme_ids": ["SCH001", "SCH002", "SCH003", "SCH004", "SCH005"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_compared"] == 5
    assert len(data["schemes"]) == 5


def test_compare_only_one_scheme():
    """Test comparison rejects only one scheme."""
    request_data = {"scheme_ids": ["SCH001"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "VALIDATION_ERROR"
    assert "at least 2" in data["detail"]["message"].lower()


def test_compare_more_than_five():
    """Test comparison rejects more than five schemes."""
    request_data = {"scheme_ids": ["SCH001", "SCH002", "SCH003", "SCH004", "SCH005", "SCH006"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "VALIDATION_ERROR"
    assert "maximum 5" in data["detail"]["message"].lower()


def test_compare_duplicate_ids():
    """Test comparison rejects duplicate scheme IDs."""
    request_data = {"scheme_ids": ["SCH001", "SCH001", "SCH002"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "VALIDATION_ERROR"
    assert "duplicate" in data["detail"]["message"].lower()


def test_compare_unknown_scheme_id():
    """Test comparison rejects unknown scheme IDs."""
    request_data = {"scheme_ids": ["SCH001", "UNKNOWN999"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "NOT_FOUND"


def test_compare_empty_scheme_ids():
    """Test comparison rejects empty scheme_ids."""
    request_data = {"scheme_ids": []}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"]["error"] == "VALIDATION_ERROR"


def test_compare_verify_all_fields():
    """Test that all comparison fields are populated with actual data."""
    request_data = {"scheme_ids": ["SCH001", "SCH002"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 200
    data = response.json()

    for scheme in data["schemes"]:
        # All required fields should be non-empty strings
        assert scheme["scheme_id"] and len(scheme["scheme_id"]) > 0
        assert scheme["scheme_name"] and len(scheme["scheme_name"]) > 0
        assert scheme["category"] and len(scheme["category"]) > 0
        assert scheme["government_level"] and len(scheme["government_level"]) > 0
        assert scheme["state"] and len(scheme["state"]) > 0
        assert scheme["benefits"] and len(scheme["benefits"]) > 0
        assert scheme["eligibility_summary"] and len(scheme["eligibility_summary"]) > 0
        assert scheme["application_process"] and len(scheme["application_process"]) > 0
        assert scheme["official_website"] and len(scheme["official_website"]) > 0
        assert isinstance(scheme["required_documents"], list)


def test_compare_official_links_preserved():
    """Test that official website and source URLs are preserved."""
    request_data = {"scheme_ids": ["SCH001", "SCH009"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 200
    data = response.json()

    for scheme in data["schemes"]:
        assert scheme["official_website"].startswith("http")


def test_compare_unavailable_fields():
    """Test that unavailable or null fields are handled gracefully."""
    # Our dataset should have all fields populated
    request_data = {"scheme_ids": ["SCH001", "SCH002"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 200
    data = response.json()

    for scheme in data["schemes"]:
        # No field should be missing from the response
        assert "scheme_id" in scheme
        assert "scheme_name" in scheme
        assert "category" in scheme
        assert "government_level" in scheme
        assert "state" in scheme
        assert "benefits" in scheme
        assert "eligibility_summary" in scheme
        assert "required_documents" in scheme
        assert "application_process" in scheme
        assert "official_website" in scheme


def test_compare_response_serialization():
    """Test that comparison response serializes correctly to JSON."""
    request_data = {"scheme_ids": ["SCH001", "SCH002"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 200
    data = response.json()

    # Should be valid JSON
    import json
    json_str = json.dumps(data)
    assert len(json_str) > 0

    # Re-parse to verify
    parsed = json.loads(json_str)
    assert parsed["success"] is True
    assert parsed["total_compared"] == 2


def test_compare_preserves_actual_benefits():
    """Test that actual benefit descriptions are used, not invented."""
    request_data = {"scheme_ids": ["SCH001", "SCH002"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 200
    data = response.json()

    scheme_map = {s["scheme_id"]: s for s in data["schemes"]}

    # SCH001 - OBC Scholarship
    sch001 = scheme_map["SCH001"]
    assert "maintenance allowance" in sch001["benefits"].lower() or "tuition" in sch001["benefits"].lower()

    # SCH002 - PM-KISAN
    sch002 = scheme_map["SCH002"]
    assert "6,000" in sch002["benefits"] or "6000" in sch002["benefits"]


def test_compare_preserves_actual_eligibility():
    """Test that actual eligibility rules are used, not invented."""
    request_data = {"scheme_ids": ["SCH001", "SCH002"]}
    response = client.post("/compare", json=request_data)

    assert response.status_code == 200
    data = response.json()

    scheme_map = {s["scheme_id"]: s for s in data["schemes"]}

    sch001 = scheme_map["SCH001"]
    # Should mention OBC category
    assert "obc" in sch001["eligibility_summary"].lower() or "category" in sch001["eligibility_summary"].lower()

    sch002 = scheme_map["SCH002"]
    # Should mention farmer/occupation
    assert "farmer" in sch002["eligibility_summary"].lower() or "occupation" in sch002["eligibility_summary"].lower()


def test_service_compare_schemes():
    """Test service function for scheme comparison."""
    manager = get_scheme_manager()
    schemes = manager.load_schemes()

    # Find SCH001 and SCH002
    sch001 = next((s for s in schemes if s.scheme_id == "SCH001"), None)
    sch002 = next((s for s in schemes if s.scheme_id == "SCH002"), None)

    assert sch001 is not None
    assert sch002 is not None

    from routes.comparison import get_scheme_comparison_item

    item1 = get_scheme_comparison_item(sch001)
    item2 = get_scheme_comparison_item(sch002)

    assert item1.scheme_id == "SCH001"
    assert item2.scheme_id == "SCH002"
    assert item1.official_website.startswith("http")
    assert len(item1.required_documents) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])