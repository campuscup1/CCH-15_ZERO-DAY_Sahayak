"""
Simulation Tests
"""

import sys
from pathlib import Path
import pytest

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from main import app
from models.schemas import UserProfile, MatchStatus, ChangeType
from services.eligibility import get_scheme_manager
from services.simulator import (
    validate_simulation_fields,
    create_simulated_profile,
    classify_change,
    identify_changed_conditions,
    run_simulation,
)

client = TestClient(app)


def test_validate_simulation_fields():
    """Test validation of simulation fields."""
    # Valid fields
    changes = {"age": 25, "annual_income": 100000, "state": "Maharashtra"}
    invalid = validate_simulation_fields(changes)
    assert invalid == []

    # Invalid fields
    changes = {"age": 25, "unknown_field": "value", "another_bad": 123}
    invalid = validate_simulation_fields(changes)
    assert "unknown_field" in invalid
    assert "another_bad" in invalid


def test_create_simulated_profile():
    """Test creating simulated profile without modifying original."""
    original = UserProfile(
        age=25,
        annual_income=500000,
        state="Maharashtra",
        education_level="Graduate",
        occupation="Engineer"
    )

    changes = {"annual_income": 100000, "age": 20}
    simulated = create_simulated_profile(original, changes)

    # Check simulated profile has changes
    assert simulated.age == 20
    assert simulated.annual_income == 100000
    assert simulated.state == "Maharashtra"  # Unchanged
    assert simulated.education_level == "Graduate"  # Unchanged

    # Check original is NOT modified
    assert original.age == 25
    assert original.annual_income == 500000


def test_create_simulated_profile_validates():
    """Test that simulated profile validates constraints."""
    original = UserProfile(age=25, annual_income=500000)

    # Invalid age should raise
    try:
        create_simulated_profile(original, {"age": -5})
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Age must be between 0 and 120" in str(e)

    # Invalid income should raise
    try:
        create_simulated_profile(original, {"annual_income": -1000})
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Annual income cannot be negative" in str(e)


def test_classify_change_new_match():
    """Test NEW_MATCH classification."""
    assert classify_change(MatchStatus.NOT_MATCH, MatchStatus.MATCH) == ChangeType.NEW_MATCH
    assert classify_change(MatchStatus.POTENTIAL_MATCH, MatchStatus.MATCH) == ChangeType.NEW_MATCH


def test_classify_change_lost_match():
    """Test LOST_MATCH classification."""
    # MATCH -> NOT_MATCH is now BECAME_NOT_MATCH (more specific)
    assert classify_change(MatchStatus.MATCH, MatchStatus.NOT_MATCH) == ChangeType.BECAME_NOT_MATCH
    # MATCH -> POTENTIAL_MATCH is LOST_MATCH
    assert classify_change(MatchStatus.MATCH, MatchStatus.POTENTIAL_MATCH) == ChangeType.LOST_MATCH


def test_classify_change_became_potential():
    """Test BECAME_POTENTIAL classification."""
    assert classify_change(MatchStatus.NOT_MATCH, MatchStatus.POTENTIAL_MATCH) == ChangeType.BECAME_POTENTIAL


def test_classify_change_became_not_match():
    """Test BECAME_NOT_MATCH classification."""
    assert classify_change(MatchStatus.MATCH, MatchStatus.NOT_MATCH) == ChangeType.BECAME_NOT_MATCH
    assert classify_change(MatchStatus.POTENTIAL_MATCH, MatchStatus.NOT_MATCH) == ChangeType.BECAME_NOT_MATCH


def test_classify_change_unchanged():
    """Test UNCHANGED classification."""
    assert classify_change(MatchStatus.MATCH, MatchStatus.MATCH) == ChangeType.UNCHANGED
    assert classify_change(MatchStatus.NOT_MATCH, MatchStatus.NOT_MATCH) == ChangeType.UNCHANGED
    assert classify_change(MatchStatus.POTENTIAL_MATCH, MatchStatus.POTENTIAL_MATCH) == ChangeType.UNCHANGED


def test_identify_changed_conditions():
    """Test identifying changed conditions."""
    from models.schemas import SchemeMatchResult, EligibilityConditionResult, ConditionStatus

    original = SchemeMatchResult(
        scheme_id="TEST001",
        scheme_name="Test Scheme",
        category="Test",
        government_level="Central",
        state="All",
        status=MatchStatus.NOT_MATCH,
        summary_reason="Failed",
        conditions=[
            EligibilityConditionResult(name="Age", status=ConditionStatus.SATISFIED, reason="OK"),
            EligibilityConditionResult(name="Income", status=ConditionStatus.NOT_SATISFIED, reason="Too high"),
        ],
        required_documents=[],
        user_missing_documents=[],
        readiness_percentage=50.0,
        official_website="https://test.com",
        source_url="https://test.com"
    )

    simulated = SchemeMatchResult(
        scheme_id="TEST001",
        scheme_name="Test Scheme",
        category="Test",
        government_level="Central",
        state="All",
        status=MatchStatus.MATCH,
        summary_reason="All satisfied",
        conditions=[
            EligibilityConditionResult(name="Age", status=ConditionStatus.SATISFIED, reason="OK"),
            EligibilityConditionResult(name="Income", status=ConditionStatus.SATISFIED, reason="Now OK"),
        ],
        required_documents=[],
        user_missing_documents=[],
        readiness_percentage=100.0,
        official_website="https://test.com",
        source_url="https://test.com"
    )

    changed = identify_changed_conditions(original, simulated)
    assert "Income" in changed
    assert "Age" not in changed  # Same status


def test_run_simulation_income_reduction():
    """Test simulation with income reduction creating new matches."""
    original = UserProfile(
        age=20,
        annual_income=500000,  # High income - likely NOT_MATCH for income-limited schemes
        state="Maharashtra",
        education_level="Undergraduate",
        category="OBC",
        occupation="Student"
    )

    changes = {"annual_income": 100000}  # Low income - should match more schemes
    result = run_simulation(original, changes)

    assert result.success is True
    assert result.total_schemes == 12
    assert result.original_profile == original
    assert result.simulated_profile.annual_income == 100000

    # Original should be unchanged
    assert result.original_profile.annual_income == 500000

    # Check summary
    assert result.changes_summary.new_matches + result.changes_summary.lost_matches + \
           result.changes_summary.became_potential + result.changes_summary.became_not_match + \
           result.changes_summary.unchanged == 12

    # Some schemes should become matches
    assert result.changes_summary.new_matches > 0 or result.changes_summary.became_potential > 0


def test_run_simulation_income_increase():
    """Test simulation with income increase losing matches."""
    original = UserProfile(
        age=20,
        annual_income=100000,  # Low income - matches SCH001
        state="Maharashtra",
        education_level="Undergraduate",
        category="OBC",
        occupation="Student"
    )

    changes = {"annual_income": 500000}  # High income - should lose SCH001
    result = run_simulation(original, changes)

    assert result.success is True
    assert result.simulated_profile.annual_income == 500000
    assert result.original_profile.annual_income == 100000

    # Should lose at least one match (SCH001) - classified as BECAME_NOT_MATCH
    became_not_match = [c for c in result.changes if c.change_type == ChangeType.BECAME_NOT_MATCH]
    assert len(became_not_match) > 0


def test_run_simulation_state_change():
    """Test simulation with state change."""
    original = UserProfile(
        age=20,
        annual_income=100000,
        state="Maharashtra",
        education_level="Undergraduate",
        category="OBC",
        occupation="Student"
    )

    changes = {"state": "Karnataka"}  # Different state
    result = run_simulation(original, changes)

    assert result.success is True
    assert result.simulated_profile.state == "Karnataka"
    assert result.original_profile.state == "Maharashtra"


def test_run_simulation_education_change():
    """Test simulation with education level change."""
    original = UserProfile(
        age=20,
        annual_income=100000,
        state="Maharashtra",
        education_level="Undergraduate",
        category="OBC",
        occupation="Student"
    )

    changes = {"education_level": "Postgraduate"}
    result = run_simulation(original, changes)

    assert result.success is True
    assert result.simulated_profile.education_level == "Postgraduate"
    assert result.original_profile.education_level == "Undergraduate"


def test_run_simulation_occupation_change():
    """Test simulation with occupation change."""
    original = UserProfile(
        age=25,
        annual_income=200000,
        state="Maharashtra",
        occupation="Student"
    )

    changes = {"occupation": "Farmer", "landholding_required": True}
    result = run_simulation(original, changes)

    assert result.success is True
    assert result.simulated_profile.occupation == "Farmer"
    assert result.simulated_profile.landholding_required is True


def test_run_simulation_multiple_changes():
    """Test simulation with multiple field changes."""
    original = UserProfile(
        age=30,
        annual_income=600000,
        state="Delhi",
        education_level="Graduate",
        occupation="Engineer"
    )

    changes = {
        "age": 22,
        "annual_income": 120000,
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "occupation": "Student",
        "category": "OBC"
    }

    result = run_simulation(original, changes)

    assert result.success is True
    assert result.simulated_profile.age == 22
    assert result.simulated_profile.annual_income == 120000
    assert result.simulated_profile.state == "Maharashtra"
    assert result.simulated_profile.education_level == "Undergraduate"
    assert result.simulated_profile.occupation == "Student"
    assert result.simulated_profile.category == "OBC"

    # Original unchanged
    assert result.original_profile.age == 30
    assert result.original_profile.annual_income == 600000


def test_run_simulation_no_changes():
    """Test simulation with no effective changes."""
    original = UserProfile(
        age=25,
        annual_income=200000,
        state="Maharashtra"
    )

    changes = {"age": 25}  # Same value
    result = run_simulation(original, changes)

    assert result.success is True
    assert result.changes_summary.unchanged == 12
    assert len(result.changes) == 0


def test_run_simulation_unknown_field():
    """Test simulation rejects unknown fields."""
    original = UserProfile(age=25, annual_income=100000)

    try:
        run_simulation(original, {"unknown_field": "value"})
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unknown simulation fields" in str(e)
        assert "unknown_field" in str(e)


def test_run_simulation_invalid_simulated_income():
    """Test simulation rejects invalid simulated income."""
    original = UserProfile(age=25, annual_income=100000)

    try:
        run_simulation(original, {"annual_income": -50000})
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Annual income cannot be negative" in str(e)


def test_run_simulation_invalid_simulated_age():
    """Test simulation rejects invalid simulated age."""
    original = UserProfile(age=25, annual_income=100000)

    try:
        run_simulation(original, {"age": 200})
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Age must be between 0 and 120" in str(e)


def test_api_simulate_endpoint():
    """Test POST /simulate endpoint."""
    request_data = {
        "profile": {
            "age": 20,
            "annual_income": 500000,
            "state": "Maharashtra",
            "education_level": "Undergraduate",
            "category": "OBC",
            "occupation": "Student"
        },
        "changes": {
            "annual_income": 100000
        }
    }

    response = client.post("/simulate", json=request_data)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["total_schemes"] == 12
    assert "original_profile" in data
    assert "simulated_profile" in data
    assert "original_summary" in data
    assert "simulated_summary" in data
    assert "changes_summary" in data
    assert "changes" in data
    assert "original_results" in data
    assert "simulated_results" in data

    # Original should be unchanged
    assert data["original_profile"]["annual_income"] == 500000
    assert data["simulated_profile"]["annual_income"] == 100000


def test_api_simulate_missing_profile():
    """Test POST /simulate with missing profile."""
    request_data = {
        "changes": {"annual_income": 100000}
    }

    response = client.post("/simulate", json=request_data)
    assert response.status_code == 400
    data = response.json()
    # Error is wrapped in detail
    assert "detail" in data
    assert data["detail"]["success"] is False
    assert data["detail"]["error"] == "VALIDATION_ERROR"


def test_api_simulate_invalid_profile():
    """Test POST /simulate with invalid profile."""
    request_data = {
        "profile": {"age": -5},
        "changes": {"annual_income": 100000}
    }

    response = client.post("/simulate", json=request_data)
    assert response.status_code in [400, 422]


def test_api_simulate_invalid_changes():
    """Test POST /simulate with invalid changes."""
    request_data = {
        "profile": {"age": 25, "annual_income": 100000},
        "changes": {"annual_income": -1000}
    }

    response = client.post("/simulate", json=request_data)
    assert response.status_code == 422


def test_api_simulate_unknown_field():
    """Test POST /simulate with unknown field in changes."""
    request_data = {
        "profile": {"age": 25, "annual_income": 100000},
        "changes": {"unknown_field": "value"}
    }

    response = client.post("/simulate", json=request_data)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"]["success"] is False
    assert data["detail"]["error"] == "INVALID_FIELDS"


def test_response_serialization():
    """Test that simulation response serializes correctly."""
    original = UserProfile(age=20, annual_income=500000, state="Maharashtra")
    changes = {"annual_income": 100000}

    result = run_simulation(original, changes)

    # Check that it can be serialized to JSON
    json_data = result.model_dump(mode='json')
    assert json_data["success"] is True
    assert json_data["total_schemes"] == 12

    # Check enum values are serialized as strings
    for change in json_data["changes"]:
        assert change["original_status"] in ["match", "potential_match", "not_match"]
        assert change["simulated_status"] in ["match", "potential_match", "not_match"]
        assert change["change_type"] in [
            "new_match", "lost_match", "became_potential",
            "became_not_match", "unchanged"
        ]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])