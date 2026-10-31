"""
API Tests for BenefitBridge Backend
"""

import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)


# ===== Health Endpoints =====

def test_root_endpoint():
    """Test GET / endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "message" in data


def test_health_endpoint():
    """Test GET /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "healthy"


# ===== Schemes Endpoints =====

def test_list_schemes():
    """Test GET /schemes endpoint."""
    response = client.get("/schemes")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "total_schemes" in data
    assert "results" in data
    assert data["total_schemes"] == 12
    assert len(data["results"]) == 12


def test_list_schemes_with_category_filter():
    """Test GET /schemes with category filter."""
    response = client.get("/schemes?category=Education")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_schemes"] == 3
    for scheme in data["results"]:
        assert scheme["category"] == "Education"


def test_list_schemes_with_government_level_filter():
    """Test GET /schemes with government_level filter."""
    response = client.get("/schemes?government_level=Central")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for scheme in data["results"]:
        assert scheme["government_level"] == "Central"


def test_list_schemes_with_state_filter():
    """Test GET /schemes with state filter."""
    response = client.get("/schemes?state=Maharashtra")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for scheme in data["results"]:
        assert scheme["state"] == "Maharashtra"


def test_list_schemes_with_search():
    """Test GET /schemes with search query."""
    response = client.get("/schemes?search=scholarship")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    for scheme in data["results"]:
        assert "scholarship" in scheme["scheme_name"].lower() or "scholarship" in scheme["description"].lower()


def test_get_scheme_valid_id():
    """Test GET /schemes/{scheme_id} with valid ID."""
    response = client.get("/schemes/SCH001")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["scheme"]["scheme_id"] == "SCH001"
    assert "eligibility_rules" in data["scheme"]
    assert "required_documents" in data["scheme"]
    assert "application_process" in data["scheme"]


def test_get_scheme_invalid_id():
    """Test GET /schemes/{scheme_id} with invalid ID."""
    response = client.get("/schemes/INVALID123")
    assert response.status_code == 404
    data = response.json()
    # Custom HTTPException returns detail as dict
    assert "detail" in data
    assert isinstance(data["detail"], dict)
    assert data["detail"]["error"] == "NOT_FOUND"


# ===== Profile Endpoints =====

def test_create_profile_valid():
    """Test POST /profile with valid data."""
    profile_data = {
        "age": 25,
        "annual_income": 500000,
        "state": "Maharashtra",
        "education_level": "Graduate",
        "occupation": "Engineer",
        "category": "OPEN"
    }
    response = client.post("/profile", json=profile_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["profile"]["age"] == 25
    assert data["profile"]["annual_income"] == 500000


def test_create_profile_invalid_age():
    """Test POST /profile with invalid age."""
    profile_data = {
        "age": 150,
        "annual_income": 500000
    }
    response = client.post("/profile", json=profile_data)
    assert response.status_code == 422  # FastAPI validation error
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
    # Check that validation error mentions age
    assert any("age" in str(d.get("loc", [])).lower() for d in data["detail"])


def test_create_profile_invalid_income():
    """Test POST /profile with invalid income."""
    profile_data = {
        "age": 25,
        "annual_income": -10000
    }
    response = client.post("/profile", json=profile_data)
    assert response.status_code == 422  # FastAPI validation error
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)
    # Check that validation error mentions income
    assert any("annual_income" in str(d.get("loc", [])).lower() for d in data["detail"])


def test_get_profile_after_create():
    """Test GET /profile after creating one."""
    # Create a profile first
    client.post("/profile", json={"age": 30, "state": "Maharashtra"})
    response = client.get("/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["profile"]["age"] == 30


def test_clear_profile():
    """Test DELETE /profile."""
    response = client.delete("/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


# ===== Match Endpoints =====

def test_match_undergraduate_profile():
    """Test POST /match with undergraduate student profile."""
    profile_data = {
        "age": 20,
        "annual_income": 150000,
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "occupation": "Student",
        "category": "OBC",
        "documents_held": ["Aadhaar Card", "Income Certificate"]
    }
    response = client.post("/match", json=profile_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_schemes"] == 12
    assert "summary" in data
    assert "results" in data
    assert len(data["results"]) == 12

    # Check summary counts
    summary = data["summary"]
    assert summary["match"] + summary["potential_match"] + summary["not_match"] == 12

    # Check that conditions are included
    for result in data["results"]:
        assert "conditions" in result
        assert len(result["conditions"]) > 0


def test_match_farmer_profile():
    """Test POST /match with farmer profile."""
    profile_data = {
        "age": 45,
        "annual_income": 200000,
        "state": "Maharashtra",
        "occupation": "Farmer",
        "landholding_required": True,
        "documents_held": ["Aadhaar Card"]
    }
    response = client.post("/match", json=profile_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_schemes"] == 12
    assert len(data["results"]) == 12

    # PM-KISAN should match
    pm_kisan = next((r for r in data["results"] if r["scheme_id"] == "SCH002"), None)
    assert pm_kisan is not None
    assert pm_kisan["status"] == "match"


def test_match_working_professional():
    """Test POST /match with working professional profile."""
    profile_data = {
        "age": 25,
        "annual_income": 600000,
        "state": "Maharashtra",
        "education_level": "Graduate",
        "occupation": "Private employee",
        "documents_held": ["Aadhaar Card", "Income Certificate"]
    }
    response = client.post("/match", json=profile_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_schemes"] == 12
    assert len(data["results"]) == 12


def test_match_incomplete_profile():
    """Test POST /match with incomplete profile."""
    profile_data = {
        "age": 22
    }
    response = client.post("/match", json=profile_data)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["total_schemes"] == 12
    assert len(data["results"]) == 12

    # Most should be potential_match due to missing info
    potential_matches = [r for r in data["results"] if r["status"] == "potential_match"]
    assert len(potential_matches) > 0


def test_match_missing_request_body():
    """Test POST /match with missing request body."""
    response = client.post("/match")
    assert response.status_code == 422  # FastAPI validation error


def test_match_invalid_profile():
    """Test POST /match with invalid profile data."""
    profile_data = {
        "age": -5,  # Invalid age
        "annual_income": 50000
    }
    response = client.post("/match", json=profile_data)
    assert response.status_code in [400, 422]  # FastAPI returns 422 for validation errors


def test_match_verify_all_schemes_evaluated():
    """Verify all 12 schemes are evaluated in matching."""
    profile_data = {
        "age": 25,
        "annual_income": 200000,
        "state": "Maharashtra"
    }
    response = client.post("/match", json=profile_data)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 12

    # All scheme IDs should be present
    scheme_ids = {r["scheme_id"] for r in data["results"]}
    expected_ids = {f"SCH{i:03d}" for i in range(1, 13)}
    assert scheme_ids == expected_ids


def test_match_condition_explanations():
    """Verify condition explanations are included in results."""
    profile_data = {
        "age": 20,
        "annual_income": 150000,
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "category": "OBC",
        "occupation": "Student"
    }
    response = client.post("/match", json=profile_data)
    assert response.status_code == 200
    data = response.json()

    # Find SCH001
    sch001 = next((r for r in data["results"] if r["scheme_id"] == "SCH001"), None)
    assert sch001 is not None
    assert sch001["status"] == "match"

    # Check conditions have explanations
    for condition in sch001["conditions"]:
        assert "name" in condition
        assert "status" in condition
        assert "reason" in condition
        assert len(condition["reason"]) > 0


# ===== CORS Headers =====

def test_cors_headers():
    """Test CORS headers are present."""
    response = client.get("/schemes", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])