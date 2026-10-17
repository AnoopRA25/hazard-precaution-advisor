
from typing import Literal
from pydantic import BaseModel, Field


PersonType = Literal["baby", "child", "elderly", "adult"]
RiskLevel = Literal["low", "medium", "high"]


class HazardAnalysis(BaseModel):
    """Output produced by the Scene Analyst."""

    setting: str
    hazards: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class RiskAssessment(BaseModel):
    """Output produced by the Risk Predictor."""

    predicted_risk: str
    risk_level: RiskLevel
    reason: str


class SafetyReport(BaseModel):
    """Final output returned to the user."""

    setting: str
    hazards: list[str]
    person_type: PersonType
    predicted_risk: str
    risk_level: RiskLevel
    precautions: list[str] = Field(min_length=2, max_length=4)
    message: str
    caregiver_alert_sent: bool = False
