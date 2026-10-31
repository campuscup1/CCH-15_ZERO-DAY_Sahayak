"""
Generate example matching responses for all four test profiles.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.eligibility import evaluate_all_schemes
from models.schemas import UserProfile, Scheme


def load_schemes():
    path = Path(__file__).parent.parent / "data" / "schemes.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Scheme(**item) for item in data]


def create_profile(profile_data):
    if "documents_held" in profile_data:
        profile_data["documents_held"] = profile_data["documents_held"] or []
    return UserProfile(**profile_data)


def print_response(profile_name, profile_data, response):
    print(f"\n{'='*80}")
    print(f"EXAMPLE RESPONSE: {profile_name}")
    print(f"{'='*80}")

    print(f"\nProfile: {json.dumps(profile_data, indent=2)}")

    print(f"\n--- MATCH RESPONSE ---")
    print(json.dumps(response.model_dump(mode='json'), indent=2, default=str))

    print(f"\n--- SUMMARY ---")
    print(f"Total schemes: {response.total_schemes}")
    print(f"MATCH: {response.summary.match}")
    print(f"POTENTIAL_MATCH: {response.summary.potential_match}")
    print(f"NOT_MATCH: {response.summary.not_match}")

    print(f"\n--- DETAILED RESULTS ---")
    for result in response.results:
        print(f"\n[{result.scheme_id}] {result.scheme_name}")
        print(f"  Status: {result.status}")
        print(f"  Reason: {result.summary_reason}")
        print(f"  Readiness: {result.readiness_percentage}%")
        print(f"  Missing docs: {result.user_missing_documents}")
        for cond in result.conditions:
            print(f"    - {cond.name}: {cond.status} - {cond.reason}")


def main():
    schemes = load_schemes()

    # Profile A: Undergraduate student
    profile_a = create_profile({
        "age": 20,
        "annual_income": 150000,
        "state": "Maharashtra",
        "education_level": "Undergraduate",
        "occupation": "Student",
        "category": "OBC",
        "documents_held": ["Aadhaar Card", "Income Certificate"]
    })
    response_a = evaluate_all_schemes(profile_a, schemes)
    print_response("PROFILE A - Undergraduate Student", {
        "age": 20, "annual_income": 150000, "state": "Maharashtra",
        "education_level": "Undergraduate", "occupation": "Student", "category": "OBC"
    }, response_a)

    # Profile B: Farmer
    profile_b = create_profile({
        "age": 45,
        "annual_income": 200000,
        "state": "Maharashtra",
        "occupation": "Farmer",
        "landholding_required": True,
        "documents_held": ["Aadhaar Card"]
    })
    response_b = evaluate_all_schemes(profile_b, schemes)
    print_response("PROFILE B - Farmer", {
        "age": 45, "annual_income": 200000, "state": "Maharashtra",
        "occupation": "Farmer", "landholding_required": True
    }, response_b)

    # Profile C: Working professional
    profile_c = create_profile({
        "age": 25,
        "annual_income": 600000,
        "state": "Maharashtra",
        "education_level": "Graduate",
        "occupation": "Private employee",
        "documents_held": ["Aadhaar Card", "Income Certificate"]
    })
    response_c = evaluate_all_schemes(profile_c, schemes)
    print_response("PROFILE C - Working Professional", {
        "age": 25, "annual_income": 600000, "state": "Maharashtra",
        "education_level": "Graduate", "occupation": "Private employee"
    }, response_c)

    # Profile D: Incomplete profile
    profile_d = create_profile({
        "age": 22
    })
    response_d = evaluate_all_schemes(profile_d, schemes)
    print_response("PROFILE D - Incomplete Profile", {
        "age": 22
    }, response_d)


if __name__ == "__main__":
    main()