"""
Simulation Routes - API endpoint for what-if eligibility simulation.
"""

from fastapi import APIRouter, HTTPException, Depends
from models.schemas import UserProfile, SimulationResponse
from services.eligibility import get_scheme_manager, SchemeManager
from services.simulator import run_simulation, validate_simulation_fields

router = APIRouter(prefix="/simulate", tags=["Simulation"])


def get_manager() -> SchemeManager:
    return get_scheme_manager()


@router.post(
    "",
    response_model=SimulationResponse,
    summary="Run what-if eligibility simulation",
    description="Simulates temporary changes to a user profile and evaluates the impact on scheme eligibility. The original profile is never modified. Results are hypothetical and do not guarantee government eligibility."
)
async def simulate_changes(
    request: dict,
    manager: SchemeManager = Depends(get_manager)
):
    """
    Run a what-if simulation.

    Request body:
    {
        "profile": { ... UserProfile fields ... },
        "changes": { "annual_income": 100000, "age": 25, ... }
    }

    Returns detailed comparison of original vs simulated eligibility.
    """
    try:
        # Parse request
        profile_data = request.get("profile", {})
        changes = request.get("changes", {})

        if not profile_data:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": "VALIDATION_ERROR", "message": "Original profile is required."}
            )

        # Validate profile
        try:
            original_profile = UserProfile(**profile_data)
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail={"success": False, "error": "VALIDATION_ERROR", "message": f"Invalid profile: {str(e)}"}
            )

        # Validate simulation fields
        invalid_fields = validate_simulation_fields(changes)
        if invalid_fields:
            raise HTTPException(
                status_code=400,
                detail={"success": False, "error": "INVALID_FIELDS", "message": f"Unknown simulation fields: {', '.join(invalid_fields)}"}
            )

        # Validate simulated values
        try:
            # Create a temporary profile to validate the simulated values
            test_dict = original_profile.model_dump(mode='python')
            test_dict.update(changes)
            UserProfile(**test_dict)
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail={"success": False, "error": "VALIDATION_ERROR", "message": f"Invalid simulated value: {str(e)}"}
            )

        # Load schemes
        try:
            schemes = manager.load_schemes()
        except FileNotFoundError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load schemes: {str(e)}")

        if not schemes:
            raise HTTPException(status_code=500, detail="No schemes available for simulation.")

        # Run simulation
        try:
            result = run_simulation(original_profile, changes, schemes)
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail={"success": False, "error": "SIMULATION_ERROR", "message": str(e)})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")