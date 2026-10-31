"""
Phase 6: What-If Eligibility Simulator

Allows users to temporarily change profile information and recalculate
all scheme matches without modifying the original profile.
"""

from typing import Dict, Any, List, Optional, Set
from copy import deepcopy

from models.schemas import (
    UserProfile,
    Scheme,
    SchemeMatchResult,
    MatchStatus,
    ChangeType,
    SimulationChangeDetail,
    SimulationSummary,
    SimulationRequest,
    SimulationResponse,
    MatchSummary,
)
from services.eligibility import evaluate_all_schemes, get_scheme_manager, SchemeManager


# Valid fields that can be simulated (must match UserProfile model)
VALID_SIMULATION_FIELDS = {
    "age",
    "annual_income",
    "state",
    "education_level",
    "occupation",
    "category",
    "gender",
    "residential_status",
    "pucca_house_owned",
    "landholding_required",
    "documents_held",
}


def validate_simulation_fields(changes: Dict[str, Any]) -> List[str]:
    """
    Validate that all fields in changes are allowed for simulation.

    Returns list of invalid field names.
    """
    invalid_fields = []
    for field in changes.keys():
        if field not in VALID_SIMULATION_FIELDS:
            invalid_fields.append(field)
    return invalid_fields


def create_simulated_profile(original: UserProfile, changes: Dict[str, Any]) -> UserProfile:
    """
    Create a new UserProfile by applying changes to the original.

    The original profile is never modified.
    """
    # Convert original to dict, then apply changes
    original_dict = original.model_dump(mode='python')
    simulated_dict = deepcopy(original_dict)

    # Apply changes
    for field, value in changes.items():
        if field in VALID_SIMULATION_FIELDS:
            simulated_dict[field] = value

    # Create new UserProfile with validation
    return UserProfile(**simulated_dict)


def classify_change(original_status: MatchStatus, simulated_status: MatchStatus) -> ChangeType:
    """
    Classify the type of change between original and simulated status.

    Rules:
    - NEW_MATCH: Original was NOT_MATCH or POTENTIAL_MATCH, simulated is MATCH
    - LOST_MATCH: Original was MATCH, simulated is POTENTIAL_MATCH (lost full match)
    - BECAME_POTENTIAL: Original was NOT_MATCH, simulated is POTENTIAL_MATCH
    - BECAME_NOT_MATCH: Original was MATCH or POTENTIAL_MATCH, simulated is NOT_MATCH
    - UNCHANGED: No change

    Priority order handles overlapping cases:
    - MATCH -> NOT_MATCH: BECAME_NOT_MATCH (more specific)
    - MATCH -> POTENTIAL_MATCH: LOST_MATCH
    - POTENTIAL_MATCH -> NOT_MATCH: BECAME_NOT_MATCH
    - NOT_MATCH -> POTENTIAL_MATCH: BECAME_POTENTIAL
    - NOT_MATCH or POTENTIAL_MATCH -> MATCH: NEW_MATCH
    """
    if original_status == simulated_status:
        return ChangeType.UNCHANGED

    # NEW_MATCH: gained full eligibility
    if original_status in [MatchStatus.NOT_MATCH, MatchStatus.POTENTIAL_MATCH] and \
       simulated_status == MatchStatus.MATCH:
        return ChangeType.NEW_MATCH

    # BECAME_NOT_MATCH: now definitively not eligible (highest priority for NOT_MATCH result)
    if original_status in [MatchStatus.MATCH, MatchStatus.POTENTIAL_MATCH] and \
       simulated_status == MatchStatus.NOT_MATCH:
        return ChangeType.BECAME_NOT_MATCH

    # LOST_MATCH: had full match, now only potential (doesn't include NOT_MATCH)
    if original_status == MatchStatus.MATCH and \
       simulated_status == MatchStatus.POTENTIAL_MATCH:
        return ChangeType.LOST_MATCH

    # BECAME_POTENTIAL: from not eligible to potentially eligible
    if original_status == MatchStatus.NOT_MATCH and \
       simulated_status == MatchStatus.POTENTIAL_MATCH:
        return ChangeType.BECAME_POTENTIAL

    # Fallback - should not happen with above logic
    return ChangeType.UNCHANGED


def identify_changed_conditions(
    original_result: SchemeMatchResult,
    simulated_result: SchemeMatchResult
) -> List[str]:
    """
    Identify which conditions changed between original and simulated results.

    Returns list of condition names that changed status.
    """
    # Create maps for easy comparison
    original_conditions = {c.name: c.status for c in original_result.conditions}
    simulated_conditions = {c.name: c.status for c in simulated_result.conditions}

    changed = []
    all_names = set(original_conditions.keys()) | set(simulated_conditions.keys())

    for name in all_names:
        orig_status = original_conditions.get(name)
        sim_status = simulated_conditions.get(name)

        if orig_status != sim_status:
            changed.append(name)

    return changed


def generate_change_explanation(
    change_type: ChangeType,
    original_status: MatchStatus,
    simulated_status: MatchStatus,
    changed_conditions: List[str],
    original_result: SchemeMatchResult,
    simulated_result: SchemeMatchResult
) -> str:
    """
    Generate a human-readable explanation for the status change.
    """
    if change_type == ChangeType.UNCHANGED:
        return "No change in eligibility status."

    explanations = []

    if change_type == ChangeType.NEW_MATCH:
        explanations.append("Your simulated profile now meets all mandatory eligibility criteria for this scheme.")

    elif change_type == ChangeType.LOST_MATCH:
        explanations.append("Your simulated profile no longer meets all mandatory eligibility criteria for this scheme.")

    elif change_type == ChangeType.BECAME_POTENTIAL:
        explanations.append("Your simulated profile has missing information that prevents full eligibility assessment.")

    elif change_type == ChangeType.BECAME_NOT_MATCH:
        explanations.append("Your simulated profile now fails one or more mandatory eligibility criteria.")

    # Add details about which conditions changed
    if changed_conditions:
        conditions_str = ", ".join(changed_conditions)
        explanations.append(f"The following conditions changed: {conditions_str}.")

        # Add specific details from simulated result
        for cond in simulated_result.conditions:
            if cond.name in changed_conditions:
                if cond.status == MatchStatus.MATCH:
                    explanations.append(f"{cond.name}: {cond.reason}")
                elif cond.status == MatchStatus.NOT_MATCH:
                    explanations.append(f"{cond.name}: {cond.reason}")

    return " ".join(explanations)


def compare_profiles(
    original_profile: UserProfile,
    simulated_profile: UserProfile,
    schemes: Optional[List[Scheme]] = None
) -> SimulationResponse:
    """
    Compare two profiles against all schemes and identify changes.

    This is the main entry point for the simulation service.
    """
    if schemes is None:
        manager = get_scheme_manager()
        schemes = manager.load_schemes()

    # Evaluate both profiles
    original_response = evaluate_all_schemes(original_profile, schemes)
    simulated_response = evaluate_all_schemes(simulated_profile, schemes)

    # Compare results scheme by scheme
    changes: List[SimulationChangeDetail] = []
    change_counts = SimulationSummary()

    # Create lookup maps
    original_map = {r.scheme_id: r for r in original_response.results}
    simulated_map = {r.scheme_id: r for r in simulated_response.results}

    for scheme in schemes:
        original_result = original_map.get(scheme.scheme_id)
        simulated_result = simulated_map.get(scheme.scheme_id)

        if not original_result or not simulated_result:
            continue

        original_status = original_result.status
        simulated_status = simulated_result.status

        change_type = classify_change(original_status, simulated_status)

        # Update summary counts
        if change_type == ChangeType.NEW_MATCH:
            change_counts.new_matches += 1
        elif change_type == ChangeType.LOST_MATCH:
            change_counts.lost_matches += 1
        elif change_type == ChangeType.BECAME_POTENTIAL:
            change_counts.became_potential += 1
        elif change_type == ChangeType.BECAME_NOT_MATCH:
            change_counts.became_not_match += 1
        elif change_type == ChangeType.UNCHANGED:
            change_counts.unchanged += 1

        # Only include in changes list if status actually changed
        if change_type != ChangeType.UNCHANGED:
            changed_conditions = identify_changed_conditions(original_result, simulated_result)
            explanation = generate_change_explanation(
                change_type,
                original_status,
                simulated_status,
                changed_conditions,
                original_result,
                simulated_result
            )

            change_detail = SimulationChangeDetail(
                scheme_id=scheme.scheme_id,
                scheme_name=scheme.scheme_name,
                original_status=original_status,
                simulated_status=simulated_status,
                change_type=change_type,
                explanation=explanation,
                changed_conditions=changed_conditions
            )
            changes.append(change_detail)

    return SimulationResponse(
        success=True,
        total_schemes=len(schemes),
        original_profile=original_profile,
        simulated_profile=simulated_profile,
        original_summary=original_response.summary,
        simulated_summary=simulated_response.summary,
        changes_summary=change_counts,
        changes=changes,
        original_results=original_response.results,
        simulated_results=simulated_response.results
    )


def run_simulation(
    original_profile: UserProfile,
    changes: Dict[str, Any],
    schemes: Optional[List[Scheme]] = None
) -> SimulationResponse:
    """
    Run a what-if simulation with the given profile and changes.

    This is the main public function for the simulation service.
    """
    # Validate simulation fields
    invalid_fields = validate_simulation_fields(changes)
    if invalid_fields:
        raise ValueError(f"Unknown simulation fields: {', '.join(invalid_fields)}. Valid fields: {', '.join(sorted(VALID_SIMULATION_FIELDS))}")

    # Create simulated profile
    simulated_profile = create_simulated_profile(original_profile, changes)

    # Run comparison
    return compare_profiles(original_profile, simulated_profile, schemes)