"""
Guided safety plan creation following clinical best practices.
"""

from typing import Dict, List
from datetime import datetime

class SafetyPlanBuilder:
    """
    Interactive safety plan builder based on Stanley-Brown model.
    Clinical standard for suicide prevention.
    """
    
    PROMPTS = {
        'warning_signs': "What are your warning signs that a crisis may be developing? (thoughts, feelings, behaviors)",
        'coping_strategies': "What can you do to take your mind off problems without contacting another person?",
        'social_contacts': "Who can you ask for help during a crisis? (Name and phone)",
        'professionals': "Mental health professionals or agencies you can contact during a crisis:",
        'environment': "How can you make your environment safer? (remove harmful items)",
        'reasons_to_live': "What are your reasons for living?"
    }
    
    @staticmethod
    def create_plan(user_responses: Dict) -> Dict:
        """
        Generate safety plan from user responses.
        Stored securely in DB for future reference.
        """
        plan = {
            'user_id': user_responses.get('user_id'),
            'created_at': datetime.utcnow().isoformat(),
            'warning_signs': user_responses.get('warning_signs', []),
            'internal_coping': user_responses.get('coping_strategies', []),
            'social_contacts': user_responses.get('social_contacts', []),
            'professional_contacts': user_responses.get('professionals', []),
            'environment_safety': user_responses.get('environment', []),
            'reasons_for_living': user_responses.get('reasons_to_live', []),
            'hotlines': user_responses.get('hotlines', {}),
            'review_schedule': 'Review and update monthly'
        }
        
        return plan
