"""
Geo-located crisis hotlines and resources.
"""

from typing import Dict, List
from geopy.geocoders import Nominatim
import phonenumbers
from datetime import datetime  # ← ADD THIS LINE


class CrisisResources:
    """
    Provides locale-appropriate crisis hotlines and resources.
    """

    HOTLINES = {
        'US': {
            'suicide_prevention': {'number': '988', 'name': 'National Suicide Prevention Lifeline'},
            'crisis_text': {'number': '741741', 'name': 'Crisis Text Line', 'sms': True},
            'veterans': {'number': '988 then press 1', 'name': 'Veterans Crisis Line'}
        },
        'IN': {
            'suicide_prevention': {'number': '+91-9152987821', 'name': 'Vandrevala Foundation'},
            'mental_health': {'number': '+91-8069878680', 'name': 'Tele MANAS'},
            'women': {'number': '+91-7827170170', 'name': 'iCall - Women\'s Helpline'}
        },
        'UK': {
            'suicide_prevention': {'number': '116123', 'name': 'Samaritans'},
            'text': {'number': '85258', 'name': 'Shout Crisis Text Line', 'sms': True}
        },
        'AU': {
            'suicide_prevention': {'number': '131114', 'name': 'Lifeline Australia'},
            'mental_health': {'number': '1300224636', 'name': 'Beyond Blue'}
        }
    }

    @staticmethod
    def get_resources(country_code: str = 'US', locale: str = 'en') -> Dict:
        """
        Fetch appropriate crisis resources based on location.
        """
        resources = CrisisResources.HOTLINES.get(
            country_code, CrisisResources.HOTLINES['US'])

        # Add emergency services
        emergency_numbers = {
            'US': '911', 'IN': '112', 'UK': '999', 'AU': '000'
        }

        resources['emergency'] = {
            'number': emergency_numbers.get(country_code, '112'),
            'name': 'Emergency Services'
        }

        return {
            'country': country_code,
            'hotlines': resources,
            'language': locale,
            'timestamp': datetime.utcnow().isoformat()
        }
