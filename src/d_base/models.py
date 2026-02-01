class CrisisSession(BaseModel):
    """Represents a crisis chat session"""
    user_id: ObjectId
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    messages: List[Dict]  # [{role, content, timestamp, risk_assessment}]
    max_risk_level: str  # IMMINENT, HIGH, MEDIUM, LOW
    escalated: bool
    escalation_time: Optional[datetime]
    outcome: Optional[str]  # RESOLVED, ESCALATED, ABANDONED
    phq9_score: Optional[int]
    gad7_score: Optional[int]

class SafetyPlan(BaseModel):
    """User's safety plan"""
    user_id: ObjectId
    created_at: datetime
    updated_at: datetime
    warning_signs: List[str]
    coping_strategies: List[str]
    social_contacts: List[Dict]  # [{name, phone, relationship}]
    professional_contacts: List[Dict]
    reasons_for_living: List[str]
    last_reviewed: datetime

class EscalationLog(BaseModel):
    """Tracks escalations to human responders"""
    session_id: str
    escalated_at: datetime
    risk_level: str
    triggers: List[str]
    responder_id: Optional[ObjectId]
    response_time: Optional[datetime]  # Time until human response
    resolution: Optional[str]
    notes: Optional[str]
