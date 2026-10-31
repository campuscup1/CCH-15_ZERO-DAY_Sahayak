"""
Phase 3: Eligibility Matching Engine

A configurable, explainable rule-based eligibility engine that evaluates
user profiles against government scheme eligibility rules.
"""

import json
from typing import Dict, Any, List, Tuple
from pathlib import Path
from models.schemas import (
    UserProfile,
    Scheme,
    MatchStatus,
    ConditionStatus,
    EligibilityConditionResult,
    SchemeMatchResult,
    MatchSummary,
    MatchResponse,
)


def evaluate_condition(
    field_name: str,
    expected_value: Any,
    actual_value: Any,
    operator: str = "eq"
) -> Tuple[bool, str]:
    """
    Evaluate a single condition against a profile field.

    Returns:
        Tuple of (is_satisfied, explanation)
    """
    if actual_value is None:
        return None, f"This information was not provided."

    # Handle different operators
    if operator == "eq":
        if isinstance(expected_value, list):
            if actual_value in expected_value:
                return True, f"Your {field_name.replace('_', ' ')} is in the required list."
            else:
                return False, f"Your {field_name.replace('_', ' ')} ({actual_value}) is not in the eligible categories."
        else:
            if actual_value == expected_value:
                return True, f"Your {field_name.replace('_', ' ')} matches the requirement."
            else:
                return False, f"Your {field_name.replace('_', ' ')} ({actual_value}) does not match required value ({expected_value})."

    elif operator == "neq":
        if actual_value != expected_value:
            return True, f"Your {field_name.replace('_', ' ')} does not match the excluded value."
        else:
            return False, f"Your {field_name.replace('_', ' ')} matches the excluded value."

    elif operator == "gt":
        if actual_value > expected_value:
            return True, f"Your {field_name.replace('_', ' ')} ({actual_value}) is greater than the required minimum ({expected_value})."
        else:
            return False, f"Your {field_name.replace('_', ' ')} ({actual_value}) must be greater than {expected_value}."

    elif operator == "gte":
        if actual_value >= expected_value:
            return True, f"Your {field_name.replace('_', ' ')} ({actual_value}) meets the minimum requirement of {expected_value}."
        else:
            return False, f"Your {field_name.replace('_', ' ')} ({actual_value}) must be at least {expected_value}."

    elif operator == "lt":
        if actual_value < expected_value:
            return True, f"Your {field_name.replace('_', ' ')} ({actual_value}) is below the maximum limit ({expected_value})."
        else:
            return False, f"Your {field_name.replace('_', ' ')} ({actual_value}) must be less than {expected_value}."

    elif operator == "lte":
        if actual_value <= expected_value:
            return True, f"Your {field_name.replace('_', ' ')} ({actual_value}) is within the allowed limit ({expected_value})."
        else:
            return False, f"Your {field_name.replace('_', ' ')} ({actual_value}) exceeds the maximum limit of {expected_value}."

    elif operator == "in":
        if actual_value in expected_value:
            return True, f"Your {field_name.replace('_', ' ')} ({actual_value}) is in the eligible list."
        else:
            return False, f"Your {field_name.replace('_', ' ')} ({actual_value}) is not in the eligible categories."

    elif operator == "not_in":
        if actual_value not in expected_value:
            return True, f"Your {field_name.replace('_', ' ')} is not in the excluded list."
        else:
            return False, f"Your {field_name.replace('_', ' ')} ({actual_value}) is not eligible."

    elif operator == "contains":
        if isinstance(expected_value, str) and expected_value.lower() in str(actual_value).lower():
            return True, f"Your {field_name.replace('_', ' ')} contains the required information."
        else:
            return False, f"Your {field_name.replace('_', ' ')} does not contain the required information."

    return False, f"Unknown operator: {operator}"


def get_condition_status(condition_result: Tuple) -> ConditionStatus:
    """Map condition evaluation result to ConditionStatus enum."""
    is_satisfied, explanation = condition_result
    if is_satisfied is None:
        return ConditionStatus.MISSING_INFORMATION
    elif is_satisfied:
        return ConditionStatus.SATISFIED
    else:
        return ConditionStatus.NOT_SATISFIED


def evaluate_scheme(
    profile: UserProfile,
    scheme: Scheme
) -> SchemeMatchResult:
    """
    Evaluate a single scheme's eligibility rules against a user profile.

    Returns a complete match result with condition details and missing documents.
    """
    rules = scheme.eligibility_rules
    conditions: List[EligibilityConditionResult] = []
    mandatory_conditions: List[EligibilityConditionResult] = []
    has_missing_info = False
    has_failed_condition = False

    # Map of field names to their display names
    field_display_names = {
        "age": "Age",
        "min_age": "Minimum Age",
        "max_age": "Maximum Age",
        "annual_income": "Annual Family Income",
        "max_income": "Maximum Annual Family Income",
        "domicile": "State/Domicile",
        "education_level": "Education Level",
        "occupation": "Occupation",
        "category": "Social Category",
        "gender": "Gender",
        "residential_status": "Residential Status",
        "pucca_house_owned": "Ownership of Pucca House",
        "landholding_required": "Land Ownership Requirement",
    }

    # Helper to get profile value and check condition
    def check_field(field_name: str, operator: str = "eq", expected_value: Any = None) -> EligibilityConditionResult:
        nonlocal has_missing_info, has_failed_condition

        actual_value = getattr(profile, field_name, None)
        display_name = field_display_names.get(field_name, field_name.replace("_", " ").title())

        result = evaluate_condition(field_name, expected_value, actual_value, operator)
        status = get_condition_status(result)

        condition = EligibilityConditionResult(
            name=display_name,
            status=status,
            reason=result[1]
        )

        # Track missing info and failures
        if status == ConditionStatus.MISSING_INFORMATION:
            has_missing_info = True
        elif status == ConditionStatus.NOT_SATISFIED:
            has_failed_condition = True

        return condition

    # Age checks - min_age and max_age are separate mandatory conditions
    if "min_age" in rules:
        val = check_field("age", "gte", rules["min_age"])
        if val.status != ConditionStatus.MISSING_INFORMATION:
            mandatory_conditions.append(val)
        conditions.append(val)

    if "max_age" in rules:
        val = check_field("age", "lte", rules["max_age"])
        if val.status != ConditionStatus.MISSING_INFORMATION:
            mandatory_conditions.append(val)
        conditions.append(val)

    # Income check - max_income is optional (null means no limit)
    if "max_income" in rules and rules["max_income"] is not None:
        val = check_field("annual_income", "lte", rules["max_income"])
        if val.status != ConditionStatus.MISSING_INFORMATION:
            mandatory_conditions.append(val)
        conditions.append(val)

    # State/Domicile check
    if "domicile" in rules and rules["domicile"] != "All":
        val = check_field("state", "eq", rules["domicile"])
        if val.status != ConditionStatus.MISSING_INFORMATION:
            mandatory_conditions.append(val)
        conditions.append(val)

    # Category check
    if "category" in rules:
        expected = rules["category"]
        if isinstance(expected, str):
            expected = [expected]
        val = check_field("category", "in", expected)
        if val.status != ConditionStatus.MISSING_INFORMATION:
            mandatory_conditions.append(val)
        conditions.append(val)

    # Education level check
    if "education_level" in rules:
        expected = rules["education_level"]
        if isinstance(expected, str):
            expected = [expected]
        val = check_field("education_level", "in", expected)
        if val.status != ConditionStatus.MISSING_INFORMATION:
            mandatory_conditions.append(val)
        conditions.append(val)

    # Occupation check
    if "occupation" in rules:
        expected = rules["occupation"]
        if isinstance(expected, str):
            expected = [expected]
        val = check_field("occupation", "in", expected)
        if val.status != ConditionStatus.MISSING_INFORMATION:
            mandatory_conditions.append(val)
        conditions.append(val)

    # Gender check
    if "gender" in rules:
        val = check_field("gender", "eq", rules["gender"])
        if val.status != ConditionStatus.MISSING_INFORMATION:
            mandatory_conditions.append(val)
        conditions.append(val)

    # Residential status check
    if "residential_status" in rules:
        val = check_field("residential_status", "eq", rules["residential_status"])
        if val.status != ConditionStatus.MISSING_INFORMATION:
            mandatory_conditions.append(val)
        conditions.append(val)

    # Pucca house ownership check
    if "pucca_house_owned" in rules:
        val = check_field("pucca_house_owned", "eq", rules["pucca_house_owned"])
        if val.status != ConditionStatus.MISSING_INFORMATION:
            mandatory_conditions.append(val)
        conditions.append(val)

    # Landholding requirement check
    if "landholding_required" in rules and rules["landholding_required"] is True:
        # This is a boolean field on profile
        actual = profile.landholding_required
        if actual is None:
            conditions.append(EligibilityConditionResult(
                name="Land Ownership Requirement",
                status=ConditionStatus.MISSING_INFORMATION,
                reason="Land ownership information was not provided."
            ))
            has_missing_info = True
        elif actual:
            conditions.append(EligibilityConditionResult(
                name="Land Ownership Requirement",
                status=ConditionStatus.SATISFIED,
                reason="You meet the land ownership requirement."
            ))
        else:
            conditions.append(EligibilityConditionResult(
                name="Land Ownership Requirement",
                status=ConditionStatus.NOT_SATISFIED,
                reason="You do not meet the land ownership requirement for this scheme."
            ))
            has_failed_condition = True

    # Calculate missing documents
    user_docs = profile.documents_held if profile.documents_held else []
    user_docs_lower = [d.lower() for d in user_docs]
    missing_docs = [
        doc for doc in scheme.required_documents
        if doc.lower() not in user_docs_lower
    ]

    # Calculate readiness percentage
    total_docs = len(scheme.required_documents)
    if total_docs == 0:
        readiness_pct = 100.0
    else:
        readiness_pct = round(((total_docs - len(missing_docs)) / total_docs) * 100, 1)

    # Determine overall match status
    if has_failed_condition:
        status = MatchStatus.NOT_MATCH
        summary_reason = "One or more mandatory eligibility conditions are not satisfied."
    elif has_missing_info:
        status = MatchStatus.POTENTIAL_MATCH
        summary_reason = "Some required information is missing to fully assess eligibility."
    else:
        status = MatchStatus.MATCH
        summary_reason = "All mandatory eligibility conditions are satisfied."

    return SchemeMatchResult(
        scheme_id=scheme.scheme_id,
        scheme_name=scheme.scheme_name,
        category=scheme.category,
        government_level=scheme.government_level,
        state=scheme.state,
        status=status,
        summary_reason=summary_reason,
        conditions=conditions,
        required_documents=scheme.required_documents,
        user_missing_documents=missing_docs,
        readiness_percentage=readiness_pct,
        official_website=scheme.official_website,
        source_url=scheme.source_url
    )


def evaluate_all_schemes(
    profile: UserProfile,
    schemes: List[Scheme]
) -> MatchResponse:
    """
    Evaluate a profile against all schemes and return a comprehensive match response.

    This is the main entry point for the eligibility engine.
    """
    results: List[SchemeMatchResult] = []

    for scheme in schemes:
        result = evaluate_scheme(profile, scheme)
        results.append(result)

    # Calculate summary statistics
    summary = MatchSummary(
        match=sum(1 for r in results if r.status == MatchStatus.MATCH),
        potential_match=sum(1 for r in results if r.status == MatchStatus.POTENTIAL_MATCH),
        not_match=sum(1 for r in results if r.status == MatchStatus.NOT_MATCH)
    )

    return MatchResponse(
        success=True,
        total_schemes=len(schemes),
        summary=summary,
        results=results
    )


# Scheme manager for loading schemes
class SchemeManager:
    """Manages loading and caching of scheme data."""

    def __init__(self, schemes_path: str = "data/schemes.json"):
        self.schemes_path = schemes_path
        self._schemes: List[Scheme] = []
        self._loaded = False

    def load_schemes(self) -> List[Scheme]:
        """Load schemes from JSON file."""
        if self._loaded:
            return self._schemes

        path = Path(self.schemes_path)
        if not path.exists():
            raise FileNotFoundError(f"Schemes file not found: {self.schemes_path}")

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._schemes = [Scheme(**item) for item in data]
        self._loaded = True
        return self._schemes

    def get_scheme_by_id(self, scheme_id: str) -> Scheme | None:
        """Get a specific scheme by its ID."""
        if not self._loaded:
            self.load_schemes()

        for scheme in self._schemes:
            if scheme.scheme_id == scheme_id:
                return scheme
        return None

    def get_all_scheme_ids(self) -> List[str]:
        """Get list of all scheme IDs."""
        if not self._loaded:
            self.load_schemes()
        return [s.scheme_id for s in self._schemes]


# Global scheme manager instance
_scheme_manager = None


def get_scheme_manager() -> SchemeManager:
    """Get or create the global scheme manager instance."""
    global _scheme_manager
    if _scheme_manager is None:
        _scheme_manager = SchemeManager()
    return _scheme_manager