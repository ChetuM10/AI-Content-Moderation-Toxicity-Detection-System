"""
Validated mental health screening questionnaires.
Auto-scoring with severity classification.
"""

from typing import Dict, List
from datetime import datetime

class PHQ9Assessment:
    """
    Patient Health Questionnaire-9 for depression screening.
    Validated tool used by clinicians worldwide.
    """
    
    QUESTIONS = [
        "Little interest or pleasure in doing things?",
        "Feeling down, depressed, or hopeless?",
        "Trouble falling/staying asleep, or sleeping too much?",
        "Feeling tired or having little energy?",
        "Poor appetite or overeating?",
        "Feeling bad about yourself or that you are a failure?",
        "Trouble concentrating on things?",
        "Moving or speaking slowly, or being fidgety/restless?",
        "Thoughts that you would be better off dead or hurting yourself?"
    ]
    
    # Scoring: 0=Not at all, 1=Several days, 2=More than half the days, 3=Nearly every day
    
    @staticmethod
    def calculate_score(responses: List[int]) -> Dict:
        """
        Auto-scoring following clinical guidelines [web:108]
        
        Args:
            responses: List of 9 integers (0-3)
        
        Returns:
            {
                'total_score': int,
                'severity': str,
                'risk_level': str,
                'recommendations': str
            }
        """
        if len(responses) != 9:
            raise ValueError("PHQ-9 requires exactly 9 responses")
        
        if not all(0 <= r <= 3 for r in responses):
            raise ValueError("Each response must be 0-3")
        
        total = sum(responses)
        
        # Severity classification (clinical standard)
        if total >= 20:
            severity = "Severe depression"
            risk = "HIGH"
            recommendation = "Immediate clinical evaluation recommended. Contact mental health professional today."
        elif total >= 15:
            severity = "Moderately severe depression"
            risk = "MEDIUM-HIGH"
            recommendation = "Clinical evaluation recommended within 1 week. Consider therapy and/or medication."
        elif total >= 10:
            severity = "Moderate depression"
            risk = "MEDIUM"
            recommendation = "Clinical evaluation recommended. Therapy and monitoring suggested."
        elif total >= 5:
            severity = "Mild depression"
            risk = "LOW"
            recommendation = "Monitor symptoms. Consider counseling or self-help resources."
        else:
            severity = "Minimal/none"
            risk = "VERY_LOW"
            recommendation = "No clinical action needed. Maintain healthy habits."
        
        # Special check: Question 9 (suicidal thoughts)
        if responses[8] >= 2:  # "More than half the days" or higher
            risk = "URGENT"
            recommendation = "⚠️ IMMEDIATE ATTENTION: Suicidal thoughts detected. Contact crisis hotline NOW: 988 (US), 9152987821 (India)"
        
        return {
            'total_score': total,
            'severity': severity,
            'risk_level': risk,
            'recommendations': recommendation,
            'timestamp': datetime.utcnow().isoformat(),
            'question_9_flag': responses[8] >= 1  # Any suicidal thought
        }

class GAD7Assessment:
    """
    Generalized Anxiety Disorder-7 screening tool.
    """
    
    QUESTIONS = [
        "Feeling nervous, anxious, or on edge?",
        "Not being able to stop or control worrying?",
        "Worrying too much about different things?",
        "Trouble relaxing?",
        "Being so restless that it's hard to sit still?",
        "Becoming easily annoyed or irritable?",
        "Feeling afraid as if something awful might happen?"
    ]
    
    @staticmethod
    def calculate_score(responses: List[int]) -> Dict:
        """Auto-scoring GAD-7 [web:108]"""
        if len(responses) != 7:
            raise ValueError("GAD-7 requires exactly 7 responses")
        
        total = sum(responses)
        
        if total >= 15:
            severity = "Severe anxiety"
            risk = "HIGH"
            recommendation = "Clinical evaluation recommended. Consider therapy and/or medication."
        elif total >= 10:
            severity = "Moderate anxiety"
            risk = "MEDIUM"
            recommendation = "Clinical consultation suggested. Therapy recommended."
        elif total >= 5:
            severity = "Mild anxiety"
            risk = "LOW"
            recommendation = "Monitor symptoms. Self-help or brief counseling may help."
        else:
            severity = "Minimal anxiety"
            risk = "VERY_LOW"
            recommendation = "No clinical action needed."
        
        return {
            'total_score': total,
            'severity': severity,
            'risk_level': risk,
            'recommendations': recommendation,
            'timestamp': datetime.utcnow().isoformat()
        }
