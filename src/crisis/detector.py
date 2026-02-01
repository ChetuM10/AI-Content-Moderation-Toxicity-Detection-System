"""
Crisis detection engine - Keyword-based version for Phase 1
"""

import re
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrisisDetector:
    """
    Real-time mental health crisis detection engine.
    Classifies user input into risk levels: LOW, MEDIUM, HIGH, IMMINENT
    """

    # DSM-5 based symptom keywords
    IMMINENT_DANGER_KEYWORDS = [
        r'\b(kill|end|die|suicide|overdose)\s+(myself|me)\b',
        r'\bgoing to (kill|hurt) myself\b',
        r'\bhave a (plan|method) to (kill|hurt|end)\b',
        r'\bgoodbye (forever|world|cruel world)\b',
        r'\bcan\'?t (take|go on) (anymore|any longer)\b',
        r'\bno (reason|point) to live\b',
        r'\bwant to (die|end it all)\b',
    ]

    HIGH_RISK_KEYWORDS = [
        r'\b(depressed|hopeless|worthless|burden)\b',
        r'\bthoughts? of (death|dying|suicide)\b',
        r'\bwish I (was|were) dead\b',
        r'\bself[ -]?harm\b',
        r'\bcutting (myself|me)\b',
        r'\b(hurting|harming) myself\b',
        r'\bbetter off dead\b',
    ]

    MEDIUM_RISK_KEYWORDS = [
        r'\b(sad|empty|numb|alone|isolated)\b',
        r'\bcan\'?t (sleep|eat|concentrate)\b',
        r'\blost (interest|pleasure) in everything\b',
        r'\bfeel like (nothing|a failure)\b',
        r'\bno (one|body) (cares|understands)\b',
    ]

    def __init__(self):
        """Initialize detector - keyword-mode only for Phase 1"""
        self.classifier = None
        logger.info("Crisis detector initialized (keyword-mode)")

    def detect_risk(self, text: str, conversation_history: List[str] = None) -> Dict:
        """
        Perform risk assessment using keyword matching only

        Returns:
            {
                'risk_level': str,
                'confidence': float,
                'triggers': List[str],
                'requires_escalation': bool,
                'recommended_action': str
            }
        """
        keyword_risk = self._check_keywords(text)

        return {
            'risk_level': keyword_risk['level'],
            'confidence': keyword_risk['confidence'],
            'triggers': keyword_risk['triggers'],
            'ml_score': 0.0,
            'requires_escalation': keyword_risk['level'] in ['IMMINENT', 'HIGH'],
            'recommended_action': self._get_action(keyword_risk['level'])
        }

    def _check_keywords(self, text: str) -> Dict:
        """Rule-based keyword detection"""
        text_lower = text.lower()

        # Check imminent danger first
        for pattern in self.IMMINENT_DANGER_KEYWORDS:
            if re.search(pattern, text_lower):
                return {
                    'level': 'IMMINENT',
                    'triggers': [pattern],
                    'confidence': 0.95
                }

        # Check high risk
        high_matches = []
        for pattern in self.HIGH_RISK_KEYWORDS:
            if re.search(pattern, text_lower):
                high_matches.append(pattern)

        if len(high_matches) >= 1:
            return {'level': 'HIGH', 'triggers': high_matches, 'confidence': 0.85}

        # Check medium risk
        medium_matches = []
        for pattern in self.MEDIUM_RISK_KEYWORDS:
            if re.search(pattern, text_lower):
                medium_matches.append(pattern)

        if len(medium_matches) >= 2:
            return {'level': 'MEDIUM', 'triggers': medium_matches, 'confidence': 0.65}
        elif len(medium_matches) == 1:
            return {'level': 'LOW', 'triggers': medium_matches, 'confidence': 0.55}

        return {'level': 'LOW', 'triggers': [], 'confidence': 0.5}

    def _get_action(self, risk_level: str) -> str:
        """Map risk level to recommended action"""
        actions = {
            'IMMINENT': 'EMERGENCY_CONTACT',
            'HIGH': 'SCHEDULE_HUMAN_CONTACT',
            'MEDIUM': 'PROVIDE_COPING_TOOLS',
            'LOW': 'CONTINUE_CHAT'
        }
        return actions.get(risk_level, 'CONTINUE_CHAT')
