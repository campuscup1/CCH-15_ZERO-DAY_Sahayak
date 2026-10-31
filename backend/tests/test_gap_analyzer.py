"""
Gap Analyzer Tests
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
from services.gap_analyzer import (
    categorize_conditions,
    generate_recommendations,
    generate_eligibility_summary,
    analyze_scheme_gaps,
    analyze_all_scheme_gaps,
)
from models.schemas import SchemeMatchResult, EligibilityConditionResult, ConditionStatus, MatchStatus

client = TestClient(app)


def test_categorize_conditions():
    """Test categorizing conditions into satisfied, failed, missing."""
    conditions = [
        EligibilityConditionResult(name="Age", status=ConditionStatus.SATISFIED, reason="OK"),
        EligibilityConditionResult(name="Income", status=ConditionStatus.NOT_SATISFIED, reason="Too high"),
        EligibilityConditionResult(name="State", status=ConditionStatus.MISSING_INFORMATION, reason="Not provided"),
    ]

    result = categorize_conditions(conditions)

    assert len(result["satisfied"]) == 1
    assert len(result["failed"]) == 1
    assert len(result["missing"]) == 1
    assert len(result["verification_required"]) == 1


def test_generate_eligibility_summary_match():
    """Test eligibility summary for MATCH status."""
    match_result = SchemeMatchResult(
        scheme_id="TEST001",
        scheme_name="Test Scheme",
        category="Test",
        government_level="Central",
        state="All",
        status=MatchStatus.MATCH,
        summary_reason="All satisfied",
        conditions=[],
        required_documents=[],
        user_missing_documents=[],
        readiness_percentage=100.0,
        official_website="https://test.com",
        source_url="https://test.com"
    )

    summary = generate_eligibility_summary(match_result)
    assert "meet all" in summary.lower()
    assert "mandatory" in summary.lower()


def test_generate_eligibility_summary_potential():
    """Test eligibility summary for POTENTIAL_MATCH status."""
    match_result = SchemeMatchResult(
        scheme_id="TEST001",
        scheme_name="Test Scheme",
        category="Test",
        government_level="Central",
        state="All",
        status=MatchStatus.POTENTIAL_MATCH,
        summary_reason="Missing info",
        conditions=[
            EligibilityConditionResult(name="Income", status=ConditionStatus.MISSING_INFORMATION, reason="Not provided"),
            EligibilityConditionResult(name="State", status=ConditionStatus.MISSING_INFORMATION, reason="Not provided"),
        ],
        required_documents=[],
        user_missing_documents=[],
        readiness_percentage=50.0,
        official_website="https://test.com",
        source_url="https://test.com"
    )

    summary = generate_eligibility_summary(match_result)
    assert "missing" in summary.lower()
    assert "2" in summary


def test_generate_eligibility_summary_not_match():
    """Test eligibility summary for NOT_MATCH status."""
    match_result = SchemeMatchResult(
        scheme_id="TEST001",
        scheme_name="Test Scheme",
        category="Test",
        government_level="Central",
        state="All",
        status=MatchStatus.NOT_MATCH,
        summary_reason="Failed",
        conditions=[
            EligibilityConditionResult(name="Age", status=ConditionStatus.NOT_SATISFIED, reason="Too old"),
            EligibilityConditionResult(name="Income", status=ConditionStatus.NOT_SATISFIED, reason="Too high"),
        ],
        required_documents=[],
        user_missing_documents=[],
        readiness_percentage=0.0,
        official_website="https://test.com",
        source_url="https://test.com"
    )

    summary = generate_eligibility_summary(match_result)
    assert "not" in summary.lower()
    assert "2" in summary


def test_generate_recommendations_missing_income():
    """Test recommendations for missing income."""
    match_result = SchemeMatchResult(
        scheme_id="TEST001",
        scheme_name="Test Scheme",
        category="Test",
        government_level="Central",
        state="All",
        status=MatchStatus.POTENTIAL_MATCH,
        summary_reason="Missing income",
        conditions=[
            EligibilityConditionResult(name="Annual Family Income", status=ConditionStatus.MISSING_INFORMATION, reason="Not provided"),
        ],
        required_documents=["Income Certificate"],
        user_missing_documents=["Income Certificate"],
        readiness_percentage=50.0,
        official_website="https://test.com",
        source_url="https://test.com"
    )

    profile = UserProfile(age=25)
    recommendations = generate_recommendations(match_result, profile)

    assert len(recommendations) > 0
    assert any("income" in r.lower() for r in recommendations)


def test_generate_recommendations_failed_age():
    """Test recommendations for failed age condition."""
    match_result = SchemeMatchResult(
        scheme_id="TEST001",
        scheme_name="Test Scheme",
        category="Test",
        government_level="Central",
        state="All",
        status=MatchStatus.NOT_MATCH,
        summary_reason="Failed age",
        conditions=[
            EligibilityConditionResult(name="Age", status=ConditionStatus.NOT_SATISFIED, reason="Too old"),
        ],
        required_documents=[],
        user_missing_documents=[],
        readiness_percentage=0.0,
        official_website="https://test.com",
        source_url="https://test.com"
    )

    profile = UserProfile(age=60)
    recommendations = generate_recommendations(match_result, profile)

    assert len(recommendations) > 0
    assert any("age" in r.lower() for r in recommendations)


def test_generate_recommendations_no_suggestions():
    """Test that at least one recommendation is always generated."""
    match_result = SchemeMatchResult(
        scheme_id="TEST001",
        scheme_name="Test Scheme",
        category="Test",
        government_level="Central",
        state="All",
        status=MatchStatus.MATCH,
        summary_reason="All satisfied",
        conditions=[],
        required_documents=[],
        user_missing_documents=[],
        readiness_percentage=100.0,
        official_website="https://test.com",
        source_url="https://test.com"
    )

    profile = UserProfile(age=25)
    recommendations = generate_recommendations(match_result, profile)

    assert len(recommendations) >= 1


def test_analyze_all_scheme_gaps():
    """Test analyzing all scheme gaps for a profile."""
    profile = UserProfile(
        age=20,
        annual_income=150000,
        state="Maharashtra",
        education_level="Undergraduate",
        category="OBC",
        occupation="Student"
    )

    result = analyze_all_scheme_gaps(profile)

    assert result.success is True
    assert result.total_schemes == 12
    assert len(result.results) == 12

    # Check structure of each result
    for gap_result in result.results:
        assert gap_result.scheme_id is not None
        assert gap_result.scheme_name is not None
        assert gap_result.eligibility_status is not None
        assert gap_result.eligibility_summary is not None
        assert isinstance(gap_result.satisfied_conditions, list)
        assert isinstance(gap_result.failed_conditions, list)
        assert isinstance(gap_result.missing_information, list)
        assert isinstance(gap_result.verification_required, list)
        assert isinstance(gap_result.recommended_actions, list)
        assert isinstance(gap_result.required_documents, list)
        assert isinstance(gap_result.missing_documents, list)


def test_analyze_all_scheme_gaps_summary_matches():
    """Test that summary matches individual results."""
    profile = UserProfile(
        age=45,
        annual_income=200000,
        state="Maharashtra",
        occupation="Farmer",
        landholding_required=True
    )

    result = analyze_all_scheme_gaps(profile)

    # Count statuses from results
    match_count = sum(1 for r in result.results if r.eligibility_status == MatchStatus.MATCH)
    potential_count = sum(1 for r in result.results if r.eligibility_status == MatchStatus.POTENTIAL_MATCH)
    not_match_count = sum(1 for r in result.results if r.eligibility_status == MatchStatus.NOT_MATCH)

    assert result.summary.match == match_count
    assert result.summary.potential_match == potential_count
    assert result.summary.not_match == not_match_count


def test_api_analyze_endpoint():
    """Test POST /analyze endpoint."""
    profile_data = {
        "age": 20,
        "annual_income": 150000,
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "occupation": "Student",
        "category": "OBC",
        "documents_held": ["Aadhaar Card", "Income Certificate"]
    }

    response = client.post("/analyze", json=profile_data)
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["total_schemes"] == 12
    assert len(data["results"]) == 12

    # Check structure
    for result in data["results"]:
        assert "scheme_id" in result
        assert "scheme_name" in result
        assert "eligibility_status" in result
        assert "eligibility_summary" in result
        assert "satisfied_conditions" in result
        assert "failed_conditions" in result
        assert "missing_information" in result
        assert "verification_required" in result
        assert "recommended_actions" in result
        assert "required_documents" in result
        assert "missing_documents" in result


def test_api_analyze_invalid_profile():
    """Test POST /analyze with invalid profile."""
    profile_data = {
        "age": -5,
        "annual_income": 50000
    }

    response = client.post("/analyze", json=profile_data)
    assert response.status_code in [400, 422]


def test_analyze_specific_scheme_match():
    """Test that a fully matching scheme produces correct analysis."""
    profile = UserProfile(
        age=20,
        annual_income=150000,
        state="Maharashtra",
        education_level="Undergraduate",
        category="OBC",
        occupation="Student"
    )

    manager = get_scheme_manager()
    schemes = manager.load_schemes()

    # SCH001 should match for this profile
    result = analyze_all_scheme_gaps(profile, schemes)

    sch001 = next((r for r in result.results if r.scheme_id == "SCH001"), None)
    assert sch001 is not None
    assert sch001.eligibility_status == MatchStatus.MATCH
    assert len(sch001.failed_conditions) == 0
    assert len(sch001.missing_information) == 0


def test_analyze_failed_condition_recommendations():
    """Test that failed conditions produce specific recommendations."""
    # Profile with high income - should fail income check for SCH001
    profile = UserProfile(
        age=20,
        annual_income=500000,  # Too high for SCH001 (max 150000)
        state="Maharashtra",
        education_level="Undergraduate",
        category="OBC",
        occupation="Student"
    )

    result = analyze_all_scheme_gaps(profile)

    sch001 = next((r for r in result.results if r.scheme_id == "SCH001"), None)
    assert sch001 is not None
    assert sch001.eligibility_status == MatchStatus.NOT_MATCH
    assert len(sch001.failed_conditions) > 0

    # Should have income-related recommendation
    income_recs = [r for r in sch001.recommended_actions if "income" in r.lower()]
    assert len(income_recs) > 0


def test_missing_documents_in_analysis():
    """Test that missing documents are included in analysis."""
    profile = UserProfile(
        age=20,
        annual_income=150000,
        state="Maharashtra",
        education_level="Undergraduate",
        category="OBC",
        occupation="Student",
        documents_held=["Aadhaar Card"]
    )

    result = analyze_all_scheme_gaps(profile)

    sch001 = next((r for r in result.results if r.scheme_id == "SCH001"), None)
    assert sch001 is not None
    assert len(sch001.missing_documents) > 0
    assert "Income Certificate" in sch001.missing_documents or "Domicile Certificate" in sch001.missing_documents

    # Should recommend preparing missing documents
    doc_recs = [r for r in sch001.recommended_actions if "document" in r.lower() or "prepare" in r.lower()]
    assert len(doc_recs) > 0


def test_empty_eligibility_rules():
    """Test gap analysis for scheme with empty eligibility rules."""
    from models.schemas import Scheme
    from services.gap_analyzer import analyze_scheme_gaps

    dummy_scheme = Scheme(
        scheme_id="TEST001",
        scheme_name="Test Scheme",
        description="Test",
        category="Test",
        government_level="Central",
        state="All",
        benefits="Test",
        eligibility_rules={},
        required_documents=[],
        application_process="Test",
        official_website="https://test.com",
        source_url="https://test.com",
        last_verified_date="2026-01-01"
    )

    match_result = SchemeMatchResult(
        scheme_id="TEST001",
        scheme_name="Test Scheme",
        category="Test",
        government_level="Central",
        state="All",
        status=MatchStatus.MATCH,
        summary_reason="All satisfied",
        conditions=[],
        required_documents=[],
        user_missing_documents=[],
        readiness_percentage=100.0,
        official_website="https://test.com",
        source_url="https://test.com"
    )

    profile = UserProfile(age=30)
    gap_result = analyze_scheme_gaps(profile, dummy_scheme, match_result)

    assert gap_result.eligibility_status == MatchStatus.MATCH
    assert len(gap_result.satisfied_conditions) == 0
    assert len(gap_result.failed_conditions) == 0
    assert len(gap_result.missing_information) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])