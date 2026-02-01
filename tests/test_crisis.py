def test_imminent_danger_detection():
    """Test that "I want to kill myself" triggers IMMINENT"""
    detector = CrisisDetector()
    result = detector.detect_risk("I want to kill myself tonight")
    assert result['risk_level'] == 'IMMINENT'

def test_phq9_scoring():
    """Test PHQ-9 calculation accuracy"""
    responses = [3, 3, 3, 3, 3, 3, 3, 3, 2]  # Severe depression
    result = PHQ9Assessment.calculate_score(responses)
    assert result['total_score'] == 26
    assert result['severity'] == "Severe depression"
    assert result['risk_level'] == "URGENT"  # Q9 = 2

def test_escalation_workflow():
    """Test human handoff triggers"""
    # Simulate HIGH risk conversation
    # Verify escalation flag set
    # Verify notification sent
    pass
