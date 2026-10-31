"""
Phase 5: Eligibility Gap Analyzer

Analyzes eligibility results from the matching engine and provides
citizen-friendly gap analysis with recommendations.
"""

from typing import List, Dict, Any, Optional
from models.schemas import (
    UserProfile,
    Scheme,
    SchemeMatchResult,
    EligibilityConditionResult,
    MatchStatus,
    ConditionStatus,
    ConditionGap,
    GapAnalysisResult,
    GapAnalysisResponse,
    MatchSummary,
)
from services.eligibility import evaluate_all_schemes, get_scheme_manager, SchemeManager


def categorize_conditions(conditions: List[EligibilityConditionResult]) -> Dict[str, List[ConditionGap]]:
    """
    Categorize conditions into satisfied, failed, missing, and verification required.

    Returns a dict with keys: satisfied, failed, missing, verification_required
    """
    satisfied = []
    failed = []
    missing = []
    verification = []

    for cond in conditions:
        gap = ConditionGap(
            name=cond.name,
            field=cond.name.lower().replace(" ", "_"),
            status=cond.status,
            reason=cond.reason
        )

        if cond.status == ConditionStatus.SATISFIED:
            satisfied.append(gap)
        elif cond.status == ConditionStatus.NOT_SATISFIED:
            failed.append(gap)
        elif cond.status == ConditionStatus.MISSING_INFORMATION:
            missing.append(gap)
            # Also add to verification if it's a field that might need verification
            verification.append(gap)

    return {
        "satisfied": satisfied,
        "failed": failed,
        "missing": missing,
        "verification_required": verification
    }


def generate_eligibility_summary(match_result: SchemeMatchResult) -> str:
    """Generate a citizen-friendly summary of the eligibility status."""
    status = match_result.status

    if status == MatchStatus.MATCH:
        return "You meet all the mandatory eligibility criteria for this scheme. Please verify the required documents before applying."
    elif status == MatchStatus.POTENTIAL_MATCH:
        missing_count = len([c for c in match_result.conditions if c.status == ConditionStatus.MISSING_INFORMATION])
        return f"You may be eligible, but {missing_count} piece(s) of required information are missing. Provide the missing details to get a complete assessment."
    else:  # NOT_MATCH
        failed_count = len([c for c in match_result.conditions if c.status == ConditionStatus.NOT_SATISFIED])
        return f"You do not currently meet the mandatory eligibility criteria. {failed_count} condition(s) are not satisfied."


def generate_recommendations(
    match_result: SchemeMatchResult,
    profile: UserProfile
) -> List[str]:
    """
    Generate citizen-friendly recommendations based on gap analysis.

    Rules:
    - Do not suggest changing genuine personal information.
    - Only recommend providing missing information.
    - Recommend document collection based on actual missing documents.
    - Avoid duplicate recommendations.
    """
    recommendations = []
    added = set()

    def add_rec(text: str):
        if text not in added:
            recommendations.append(text)
            added.add(text)

    # Based on missing information
    missing_conditions = [c for c in match_result.conditions if c.status == ConditionStatus.MISSING_INFORMATION]
    for cond in missing_conditions:
        field = cond.name.lower()
        if "income" in field:
            add_rec("Provide your annual family income to check if you meet the income criteria.")
        elif "age" in field:
            add_rec("Confirm your age to verify if you fall within the eligible age range.")
        elif "state" in field or "domicile" in field:
            add_rec("Provide your state of domicile to check geographic eligibility.")
        elif "category" in field or "social category" in field:
            add_rec("Specify your social category (e.g., OBC, SC, ST, EWS, OPEN) to verify category-based eligibility.")
        elif "education" in field:
            add_rec("Provide your current or highest education level.")
        elif "occupation" in field:
            add_rec("Provide your current occupation.")
        elif "gender" in field:
            add_rec("Provide your gender if this scheme has gender-specific criteria.")
        elif "land" in field:
            add_rec("Confirm whether you own agricultural land.")
        elif "house" in field or "pucca" in field:
            add_rec("Confirm whether your family owns a pucca (permanent) house.")
        else:
            add_rec(f"Provide {cond.name.lower()} information for complete eligibility assessment.")

    # Based on failed conditions
    failed_conditions = [c for c in match_result.conditions if c.status == ConditionStatus.NOT_SATISFIED]
    for cond in failed_conditions:
        field = cond.name.lower()
        if "income" in field:
            add_rec("Your income exceeds the scheme's limit. Check if you qualify for other schemes with higher income limits.")
        elif "age" in field:
            if "minimum" in cond.reason.lower():
                add_rec("You are below the minimum age required. Check if the scheme has age relaxations or consider other schemes.")
            else:
                add_rec("You are above the maximum age limit. Look for other schemes without upper age limits.")
        elif "category" in field:
            add_rec("Your category does not match this scheme's criteria. Check if you belong to any other eligible category or look for universal schemes.")
        elif "education" in field:
            add_rec("Your education level does not match the scheme requirements. Check for schemes matching your education level.")
        elif "occupation" in field:
            add_rec("Your occupation does not match the scheme's target group. Look for schemes targeting your occupation.")
        elif "land" in field:
            add_rec("This scheme requires land ownership. Consider schemes for landless farmers or agricultural workers.")
        elif "house" in field or "pucca" in field:
            add_rec("This scheme requires you not to own a pucca house. You may still qualify for other housing schemes.")
        elif "gender" in field:
            add_rec("This scheme is for a specific gender. Look for gender-neutral or your-gender-specific schemes.")
        else:
            add_rec(f"The condition '{cond.name}' is not satisfied. Review the scheme requirements carefully.")

    # Based on missing documents
    if match_result.user_missing_documents:
        docs_list = ", ".join(match_result.user_missing_documents)
        add_rec(f"Prepare the following documents before applying: {docs_list}.")

    # If no specific recommendations
    if not recommendations:
        if match_result.status == MatchStatus.MATCH:
            add_rec("All eligibility criteria are met. Gather the required documents and apply through the official portal.")
        else:
            add_rec("Review the scheme requirements and check for other applicable schemes.")

    return recommendations


def analyze_scheme_gaps(
    profile: UserProfile,
    scheme: Scheme,
    match_result: SchemeMatchResult
) -> GapAnalysisResult:
    """
    Perform detailed gap analysis for a single scheme.

    Uses the existing match result to categorize conditions and generate recommendations.
    """
    categorized = categorize_conditions(match_result.conditions)

    # Generate eligibility summary
    eligibility_summary = generate_eligibility_summary(match_result)

    # Generate recommendations
    recommendations = generate_recommendations(match_result, profile)

    return GapAnalysisResult(
        scheme_id=scheme.scheme_id,
        scheme_name=scheme.scheme_name,
        eligibility_status=match_result.status,
        eligibility_summary=eligibility_summary,
        satisfied_conditions=categorized["satisfied"],
        failed_conditions=categorized["failed"],
        missing_information=categorized["missing"],
        verification_required=categorized["verification_required"],
        recommended_actions=recommendations,
        required_documents=match_result.required_documents,
        missing_documents=match_result.user_missing_documents
    )


def analyze_all_scheme_gaps(
    profile: UserProfile,
    schemes: Optional[List[Scheme]] = None
) -> GapAnalysisResponse:
    """
    Perform gap analysis for all schemes against a profile.

    If schemes is not provided, loads all schemes from the data file.
    """
    if schemes is None:
        manager = get_scheme_manager()
        schemes = manager.load_schemes()

    # First, get the match results
    match_response = evaluate_all_schemes(profile, schemes)

    # Analyze gaps for each scheme
    gap_results = []
    for match_result in match_response.results:
        # Find the corresponding scheme
        scheme = next((s for s in schemes if s.scheme_id == match_result.scheme_id), None)
        if scheme:
            gap_result = analyze_scheme_gaps(profile, scheme, match_result)
            gap_results.append(gap_result)

    return GapAnalysisResponse(
        success=True,
        total_schemes=len(schemes),
        summary=match_response.summary,
        results=gap_results
    )