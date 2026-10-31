import json
from models.schemas import Scheme, UserProfile

def test_phase2():
    print("--- Running Phase 2 Validation Test ---")

    # 1. Load schemes.json
    with open("data/schemes.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} schemes from data/schemes.json.")

    # 2. Validate every scheme against Pydantic Scheme model
    scheme_ids = set()
    for idx, item in enumerate(data):
        try:
            scheme = Scheme(**item)
            if scheme.scheme_id in scheme_ids:
                raise ValueError(f"Duplicate scheme_id found: {scheme.scheme_id}")
            scheme_ids.add(scheme.scheme_id)
            print(f"  [PASS] {scheme.scheme_id}: {scheme.scheme_name}")
        except Exception as e:
            print(f"  [FAIL] Scheme at index {idx} failed validation: {e}")
            raise e

    print(f"\nAll {len(scheme_ids)} schemes successfully validated!")

    # 3. Test UserProfile validation
    profile_data = {
        "age": 21,
        "annual_income": 120000.0,
        "state": "Maharashtra",
        "category": "OBC",
        "documents_held": ["Aadhaar Card", "Income Certificate"]
    }
    profile = UserProfile(**profile_data)
    print(f"\nUserProfile successfully validated: {profile.model_dump()}")

    # Test invalid age
    try:
        UserProfile(age=150)
    except ValueError as e:
        print(f"  [PASS] Invalid age correctly caught: {e}")

    # Test invalid income
    try:
        UserProfile(annual_income=-500)
    except ValueError as e:
        print(f"  [PASS] Invalid income correctly caught: {e}")

    print("\nPHASE 2 VALIDATION COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    test_phase2()
