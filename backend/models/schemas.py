from enum import Enum
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator, model_validator


class MatchStatus(str, Enum):
    MATCH = "match"
    POTENTIAL_MATCH = "potential_match"
    NOT_MATCH = "not_match"


class ConditionStatus(str, Enum):
    SATISFIED = "satisfied"
    NOT_SATISFIED = "not_satisfied"
    MISSING_INFORMATION = "missing_information"


class UserProfile(BaseModel):
    age: Optional[int] = Field(None, description="Age in years (0-120)")
    annual_income: Optional[float] = Field(None, description="Annual family income in INR")
    state: Optional[str] = Field(None, description="State of domicile")
    education_level: Optional[str] = Field(None, description="Current or highest education level")
    occupation: Optional[str] = Field(None, description="Current occupation")
    category: Optional[str] = Field(None, description="Social category e.g. OPEN, OBC, SC, ST, EWS")
    gender: Optional[str] = Field(None, description="Gender e.g. Male, Female, Other")
    residential_status: Optional[str] = Field(None, description="Urban or Rural")
    pucca_house_owned: Optional[bool] = Field(None, description="Whether family owns a pucca house")
    landholding_required: Optional[bool] = Field(None, description="Whether user owns agricultural land")
    documents_held: Optional[List[str]] = Field(default_factory=list, description="List of documents user currently possesses")

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and (v < 0 or v > 120):
            raise ValueError("Age must be between 0 and 120 years")
        return v

    @field_validator("annual_income")
    @classmethod
    def validate_income(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v < 0:
            raise ValueError("Annual income cannot be negative")
        return v


class EligibilityRule(BaseModel):
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    max_income: Optional[float] = None
    domicile: Optional[str] = None
    gender: Optional[str] = None
    category: Optional[Union[str, List[str]]] = None
    education_level: Optional[Union[str, List[str]]] = None
    occupation: Optional[Union[str, List[str]]] = None
    residential_status: Optional[str] = None
    pucca_house_owned: Optional[bool] = None
    landholding_required: Optional[bool] = None


class EligibilityConditionResult(BaseModel):
    name: str
    status: ConditionStatus
    reason: str


class Scheme(BaseModel):
    scheme_id: str
    scheme_name: str
    description: str
    category: str
    government_level: str
    state: Optional[str] = "All"
    benefits: str
    eligibility_rules: Dict[str, Any]
    required_documents: List[str]
    application_process: str
    official_website: str
    source_url: str
    last_verified_date: str


class SchemeMatchResult(BaseModel):
    scheme_id: str
    scheme_name: str
    category: str
    government_level: str
    state: Optional[str] = "All"
    status: MatchStatus
    summary_reason: str
    conditions: List[EligibilityConditionResult]
    required_documents: List[str]
    user_missing_documents: List[str]
    readiness_percentage: float
    official_website: str
    source_url: str


class MatchSummary(BaseModel):
    match: int = 0
    potential_match: int = 0
    not_match: int = 0


class MatchResponse(BaseModel):
    success: bool = True
    total_schemes: int
    summary: MatchSummary
    results: List[SchemeMatchResult]


class DocumentCheckRequest(BaseModel):
    scheme_id: str
    documents_held: List[str]


class DocumentReadinessResponse(BaseModel):
    success: bool = True
    scheme_id: str
    scheme_name: str
    required_documents: List[str]
    documents_held: List[str]
    missing_documents: List[str]
    readiness_percentage: float
    message: str


class SimulationRequest(BaseModel):
    original_profile: UserProfile
    simulated_profile: UserProfile


class StatusChangeDetail(BaseModel):
    scheme_id: str
    scheme_name: str
    original_status: MatchStatus
    simulated_status: MatchStatus
    triggering_conditions: List[str]
    explanation: str


class SimulationResponse(BaseModel):
    success: bool = True
    original_summary: MatchSummary
    simulated_summary: MatchSummary
    changed_schemes_count: int
    changes: List[StatusChangeDetail]
    original_results: List[SchemeMatchResult]
    simulated_results: List[SchemeMatchResult]


class SchemeComparisonRequest(BaseModel):
    scheme_ids: List[str]


class SchemeComparisonItem(BaseModel):
    scheme_id: str
    scheme_name: str
    category: str
    government_level: str
    state: str
    benefits: str
    eligibility_summary: str
    required_documents: List[str]
    application_process: str
    official_website: str


class SchemeComparisonResponse(BaseModel):
    success: bool = True
    total_compared: int
    schemes: List[SchemeComparisonItem]


# Gap Analysis Models
class ConditionGap(BaseModel):
    """Represents a single condition with its gap analysis."""
    name: str
    field: str
    status: ConditionStatus
    reason: str
    expected: Optional[Any] = None
    actual: Optional[Any] = None


class GapAnalysisResult(BaseModel):
    """Gap analysis for a single scheme."""
    scheme_id: str
    scheme_name: str
    eligibility_status: MatchStatus
    eligibility_summary: str
    satisfied_conditions: List[ConditionGap]
    failed_conditions: List[ConditionGap]
    missing_information: List[ConditionGap]
    verification_required: List[ConditionGap]
    recommended_actions: List[str]
    required_documents: List[str]
    missing_documents: List[str]


class GapAnalysisResponse(BaseModel):
    """Response for gap analysis across all schemes."""
    success: bool = True
    total_schemes: int
    summary: MatchSummary
    results: List[GapAnalysisResult]


# Simulation Models
class ChangeType(str, Enum):
    """Types of eligibility status changes."""
    NEW_MATCH = "new_match"
    LOST_MATCH = "lost_match"
    BECAME_POTENTIAL = "became_potential"
    BECAME_NOT_MATCH = "became_not_match"
    UNCHANGED = "unchanged"


class SimulationChangeDetail(BaseModel):
    """Detail of a single scheme's status change in simulation."""
    scheme_id: str
    scheme_name: str
    original_status: MatchStatus
    simulated_status: MatchStatus
    change_type: ChangeType
    explanation: str
    changed_conditions: List[str]


class SimulationSummary(BaseModel):
    """Summary of simulation changes across all schemes."""
    new_matches: int = 0
    lost_matches: int = 0
    became_potential: int = 0
    became_not_match: int = 0
    unchanged: int = 0


class SimulationRequest(BaseModel):
    """Request for what-if simulation."""
    profile: UserProfile
    changes: Dict[str, Any]


class SimulationResponse(BaseModel):
    """Response for what-if simulation."""
    success: bool = True
    total_schemes: int
    original_profile: UserProfile
    simulated_profile: UserProfile
    original_summary: MatchSummary
    simulated_summary: MatchSummary
    changes_summary: SimulationSummary
    changes: List[SimulationChangeDetail]
    original_results: List[SchemeMatchResult]
    simulated_results: List[SchemeMatchResult]
