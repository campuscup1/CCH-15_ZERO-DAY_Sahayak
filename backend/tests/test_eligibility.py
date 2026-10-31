"""
Phase 3: Test Eligibility Engine

Tests the rule-based matching engine with multiple profiles.
"""

import json
from pathlib import Path
from services.eligibility import evaluate_all_schemes, get_scheme_manager
from models.schemas import UserProfile


from models.schemas import Scheme

def load_schemes():
    """Load schemes from JSON file as Pydantic models."""
    path = Path("data/schemes.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Scheme(**item) for item in data]


def create_profile(profile_data):
    """Create a UserProfile from dictionary."""
    # Handle documents_held properly
    if "documents_held" in profile_data:
        profile_data["documents_held"] = profile_data["documents_held"] or []
    return UserProfile(**profile_data)


def test_profile_a():
    """Test Profile A: Undergraduate student with low family income."""
    print("=== Testing Profile A: Undergraduate Student ===")

    profile_data = {
        "age": 20,
        "annual_income": 150000,
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "occupation": "Student",
        "category": "OBC",
        "documents_held": ["Aadhaar Card", "Income Certificate"]
    }

    profile = create_profile(profile_data)

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    print(f"Total schemes evaluated: {results.total_schemes}")
    print(f"Summary: {results.summary.model_dump()}")

    matches = [r for r in results.results if r.status == "match"]
    potential_matches = [r for r in results.results if r.status == "potential_match"]
    not_matches = [r for r in results.results if r.status == "not_match"]

    print(f"MATCH schemes: {len(matches)}")
    for m in matches[:5]:
        print(f"  - {m.scheme_name} (ID: {m.scheme_id})")

    print(f"POTENTIAL_MATCH schemes: {len(potential_matches)}")
    for p in potential_matches[:5]:
        print(f"  - {p.scheme_name} (ID: {p.scheme_id})")

    print(f"NOT_MATCH schemes: {len(not_matches)}")

    return results


def test_profile_b():
    """Test Profile B: Farmer."""
    print("\n=== Testing Profile B: Farmer ===")

    profile_data = {
        "age": 45,
        "annual_income": 200000,
        "state": "Maharashtra",
        "occupation": "Farmer",
        "landholding_required": True,
        "documents_held": ["Aadhaar Card"]
    }

    profile = create_profile(profile_data)

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    print(f"Total schemes evaluated: {results.total_schemes}")
    print(f"Summary: {results.summary.model_dump()}")

    matches = [r for r in results.results if r.status == "match"]
    potential_matches = [r for r in results.results if r.status == "potential_match"]
    not_matches = [r for r in results.results if r.status == "not_match"]

    print(f"MATCH schemes: {len(matches)}")
    for m in matches[:5]:
        print(f"  - {m.scheme_name} (ID: {m.scheme_id})")

    print(f"POTENTIAL_MATCH schemes: {len(potential_matches)}")
    for p in potential_matches[:5]:
        print(f"  - {p.scheme_name} (ID: {p.scheme_id})")

    print(f"NOT_MATCH schemes: {len(not_matches)}")

    return results


def test_profile_c():
    """Test Profile C: Working professional."""
    print("\n=== Testing Profile C: Working Professional ===")

    profile_data = {
        "age": 25,
        "annual_income": 600000,
        "state": "Maharashtra",
        "education_level": "Graduate",
        "occupation": "Private employee",
        "documents_held": ["Aadhaar Card", "Income Certificate"]
    }

    profile = create_profile(profile_data)

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    print(f"Total schemes evaluated: {results.total_schemes}")
    print(f"Summary: {results.summary.model_dump()}")

    matches = [r for r in results.results if r.status == "match"]
    potential_matches = [r for r in results.results if r.status == "potential_match"]
    not_matches = [r for r in results.results if r.status == "not_match"]

    print(f"MATCH schemes: {len(matches)}")
    for m in matches[:5]:
        print(f"  - {m.scheme_name} (ID: {m.scheme_id})")

    print(f"POTENTIAL_MATCH schemes: {len(potential_matches)}")
    for p in potential_matches[:5]:
        print(f"  - {p.scheme_name} (ID: {p.scheme_id})")

    print(f"NOT_MATCH schemes: {len(not_matches)}")

    return results


def test_profile_d():
    """Test Profile D: Incomplete profile."""
    print("\n=== Testing Profile D: Incomplete Profile ===")

    profile_data = {
        "age": 22
    }

    profile = create_profile(profile_data)

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    print(f"Total schemes evaluated: {results.total_schemes}")
    print(f"Summary: {results.summary.model_dump()}")

    matches = [r for r in results.results if r.status == "match"]
    potential_matches = [r for r in results.results if r.status == "potential_match"]
    not_matches = [r for r in results.results if r.status == "not_match"]

    print(f"MATCH schemes: {len(matches)}")
    for m in matches[:5]:
        print(f"  - {m.scheme_name} (ID: {m.scheme_id})")

    print(f"POTENTIAL_MATCH schemes: {len(potential_matches)}")
    for p in potential_matches[:5]:
        print(f"  - {p.scheme_name} (ID: {p.scheme_id})")

    print(f"NOT_MATCH schemes: {len(not_matches)}")

    return results


def test_missing_income_handling():
    """Test handling of missing income information."""
    print("\n=== Testing Missing Income Handling ===")

    profile_data = {
        "age": 30,
        "state": "Maharashtra",
        "education_level": "Graduate",
        "occupation": "Engineer"
    }

    profile = create_profile(profile_data)

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    income_missing_count = sum(
        1 for r in results.results
        if any(c.status == "missing_information" and "Income" in c.name for c in r.conditions)
    )

    print(f"Schemes with missing income info: {income_missing_count}")
    print(f"Total schemes evaluated: {results.total_schemes}")

    return results


def test_null_max_income():
    """Test schemes with null max_income (no limit)."""
    print("\n=== Testing Null Max Income ===")

    profile_data = {
        "age": 40,
        "state": "All",
        "occupation": "Farmer"
    }

    profile = create_profile(profile_data)

    schemes = load_schemes()
    results = evaluate_all_schemes(profile, schemes)

    for result in results.results:
        if result.scheme_id == "SCH002":
            print(f"PM-KISAN scheme status: {result.status}")
            print(f"Conditions:")
            for c in result.conditions:
                print(f"  - {c.name}: {c.status} - {c.reason}")
            break

    return results


def run_all_tests():
    """Run all test functions."""
    print("Running Phase 3 Eligibility Engine Tests\n")
    print("=" * 60)

    test_profile_a()
    test_profile_b()
    test_profile_c()
    test_profile_d()

    test_missing_income_handling()
    test_null_max_income()

    print("\n" + "=" * 60)
    print("All tests completed!")


if __name__ == "__main__":
    run_all_tests()