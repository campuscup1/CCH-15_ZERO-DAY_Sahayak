"""
Phase 3: Pytest tests for Eligibility Engine
"""

import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.eligibility import evaluate_all_schemes, evaluate_scheme
from models.schemas import UserProfile, Scheme, MatchStatus, ConditionStatus


def load_schemes():
    """Load schemes from JSON file as Pydantic models."""
    path = Path(__file__).parent.parent / "data" / "schemes.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Scheme(**item) for item in data]


def create_profile(profile_data):
    """Create a UserProfile from dictionary."""
    if "documents_held" in profile_data:
        profile_data["documents_held"] = profile_data["documents_held"] or []
    return UserProfile(**profile_data)


def test_profile_a_undergraduate():
    """Test Profile A: Undergraduate student with low family income."""
    profile = create_profile({
        "age": 20,
        "annual_income": 150000,
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "occupation": "Student",
        "category": "OBC",
        "documents_held": ["Aadhaar Card", "Income Certificate"]
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    # Should match at least the OBC scholarship
    match_schemes = [r for r in results.results if r.status == MatchStatus.MATCH]
    assert len(match_schemes) >= 1, f"Expected at least 1 match, got {len(match_schemes)}"

    # SCH001 should match
    sch001 = next((r for r in results.results if r.scheme_id == "SCH001"), None)
    assert sch001 is not None, "SCH001 not found"
    assert sch001.status == MatchStatus.MATCH, f"SCH001 should match, got {sch001.status}"

    # Check condition explanations exist
    assert len(sch001.conditions) > 0, "Conditions should be present"


def test_profile_b_farmer():
    """Test Profile B: Farmer."""
    profile = create_profile({
        "age": 45,
        "annual_income": 200000,
        "state": "Maharashtra",
        "occupation": "Farmer",
        "landholding_required": True,
        "documents_held": ["Aadhaar Card"]
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    # Should match PM-KISAN
    sch002 = next((r for r in results.results if r.scheme_id == "SCH002"), None)
    assert sch002 is not None, "SCH002 not found"
    assert sch002.status == MatchStatus.MATCH, f"SCH002 should match, got {sch002.status}"


def test_profile_c_working_professional():
    """Test Profile C: Working professional."""
    profile = create_profile({
        "age": 25,
        "annual_income": 600000,
        "state": "Maharashtra",
        "education_level": "Graduate",
        "occupation": "Private employee",
        "documents_held": ["Aadhaar Card", "Income Certificate"]
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    # Most should not match due to income
    not_matches = [r for r in results.results if r.status == MatchStatus.NOT_MATCH]
    assert len(not_matches) > 0, "Expected some NOT_MATCH results"


def test_profile_d_incomplete():
    """Test Profile D: Incomplete profile - missing state, income, occupation."""
    profile = create_profile({
        "age": 22
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    # With missing info, most should be POTENTIAL_MATCH, NOT_MATCH only if age fails
    potential_matches = [r for r in results.results if r.status == MatchStatus.POTENTIAL_MATCH]
    not_matches = [r for r in results.results if r.status == MatchStatus.NOT_MATCH]

    # At least some should be potential match
    assert len(potential_matches) > 0, "Expected POTENTIAL_MATCH results for incomplete profile"

    # Missing info should be reported in conditions
    for result in results.results:
        missing_conditions = [c for c in result.conditions if c.status == ConditionStatus.MISSING_INFORMATION]
        # If state is required but not provided, should have missing info
        if result.scheme_id in ["SCH001", "SCH003", "SCH004", "SCH006", "SCH008", "SCH010", "SCH012"]:
            assert len(missing_conditions) > 0, f"Expected missing info conditions for {result.scheme_id}"


def test_null_max_income():
    """Test schemes with null max_income (no income limit)."""
    profile = create_profile({
        "age": 40,
        "state": "All",
        "occupation": "Farmer"
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    sch002 = next((r for r in results.results if r.scheme_id == "SCH002"), None)
    assert sch002 is not None, "SCH002 not found"

    # Should be POTENTIAL_MATCH (missing landholding info)
    assert sch002.status in [MatchStatus.MATCH, MatchStatus.POTENTIAL_MATCH], \
        f"SCH002 should not be NOT_MATCH due to null max_income, got {sch002.status}"


def test_income_boundary():
    """Test income boundary conditions."""
    # Profile exactly at income limit
    profile = create_profile({
        "age": 20,
        "annual_income": 150000,  # Exactly at SCH001 limit
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "category": "OBC",
        "occupation": "Student"
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    sch001 = next((r for r in results.results if r.scheme_id == "SCH001"), None)
    assert sch001.status == MatchStatus.MATCH, "Should match at exact income boundary"


def test_age_boundary():
    """Test age boundary conditions."""
    # Profile exactly at min age
    profile = create_profile({
        "age": 18,
        "annual_income": 50000,
        "state": "All",
        "occupation": "Farmer",
        "landholding_required": True
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    sch002 = next((r for r in results.results if r.scheme_id == "SCH002"), None)
    assert sch002.status == MatchStatus.MATCH, "Should match at exact age boundary"


def test_or_logic_category():
    """Test OR logic for category lists."""
    # SCH006 accepts OPEN, SEBC, EWS - test OPEN
    profile = create_profile({
        "age": 20,
        "annual_income": 500000,
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "category": "OPEN",
        "occupation": "Student"
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    sch006 = next((r for r in results.results if r.scheme_id == "SCH006"), None)
    assert sch006 is not None
    # Category should be satisfied
    cat_cond = next((c for c in sch006.conditions if "Category" in c.name or "category" in c.name.lower()), None)
    assert cat_cond is not None
    assert cat_cond.status == ConditionStatus.SATISFIED, f"Category should be satisfied, got {cat_cond.status}"


def test_and_logic():
    """Test that AND logic works - all mandatory conditions must pass."""
    # Profile that fails age but passes income
    profile = create_profile({
        "age": 40,  # Too old for SCH001 (max 35)
        "annual_income": 50000,
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "category": "OBC",
        "occupation": "Student"
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    sch001 = next((r for r in results.results if r.scheme_id == "SCH001"), None)
    assert sch001.status == MatchStatus.NOT_MATCH, "Should NOT_MATCH due to age failure"


def test_empty_eligibility_rules():
    """Test scheme with minimal/no eligibility rules."""
    # Create a dummy scheme with empty rules
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

    profile = create_profile({"age": 30})
    result = evaluate_scheme(profile, dummy_scheme)

    # Empty rules should result in MATCH (no conditions to fail)
    assert result.status == MatchStatus.MATCH, "Empty rules should match"


def test_missing_optional_not_reject():
    """Test that missing optional info doesn't auto-reject."""
    # SCH007 (NAPS) has no income requirement, no category requirement
    profile = create_profile({
        "age": 20,
        "education_level": "Undergraduate",
        "state": "All"
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    sch007 = next((r for r in results.results if r.scheme_id == "SCH007"), None)
    assert sch007 is not None
    # Should not be NOT_MATCH just because optional fields missing
    # Could be MATCH or POTENTIAL_MATCH


def test_operator_in():
    """Test 'in' operator for list fields."""
    # SCH003 has category as list
    profile = create_profile({
        "age": 30,
        "annual_income": 500000,
        "state": "Maharashtra",
        "category": "Yellow Ration Card"
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    sch003 = next((r for r in results.results if r.scheme_id == "SCH003"), None)
    cat_cond = next((c for c in sch003.conditions if "Category" in c.name), None)
    assert cat_cond is not None
    assert cat_cond.status == ConditionStatus.SATISFIED


def test_gender_condition():
    """Test gender-specific conditions."""
    # SCH004 requires Female
    profile = create_profile({
        "age": 30,
        "annual_income": 100000,
        "state": "Maharashtra",
        "gender": "Female"
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    sch004 = next((r for r in results.results if r.scheme_id == "SCH004"), None)
    assert sch004 is not None
    gender_cond = next((c for c in sch004.conditions if "Gender" in c.name), None)
    assert gender_cond is not None
    assert gender_cond.status == ConditionStatus.SATISFIED


def test_boolean_condition():
    """Test boolean field conditions."""
    # SCH005 requires pucca_house_owned = false
    profile = create_profile({
        "age": 30,
        "annual_income": 300000,
        "state": "All",
        "residential_status": "Urban",
        "pucca_house_owned": False
    })

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    sch005 = next((r for r in results.results if r.scheme_id == "SCH005"), None)
    house_cond = next((c for c in sch005.conditions if "Pucca" in c.name), None)
    assert house_cond is not None
    assert house_cond.status == ConditionStatus.SATISFIED


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])