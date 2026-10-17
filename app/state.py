
from typing import TypedDict, Literal


class HazardState(TypedDict, total=False):
    # User input
    image_path: str
    person_type: Literal["baby", "child", "elderly", "adult"]
    language: Literal["English", "Kannada", "Hindi"]

    # Scene Analyst output
    setting: str
    hazards: list[str]
    confidence: float

    # Risk Predictor output
    predicted_risk: str
    risk_level: Literal["low", "medium", "high"]
    reason: str

    # Safety Advisor output
    precautions: list[str]
    guideline_sources: list[str]

    # Reporter output
    message: str
    caregiver_alert_sent: bool

    # Workflow control
    retry_count: int
    needs_retry: bool
    error: str
