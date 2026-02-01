"""
Conversational crisis support bot with escalation logic.
"""

from groq import Groq
import logging

logger = logging.getLogger(__name__)

class CrisisChatbot:
    """
    Empathetic chatbot for mental health support.
    Follows evidence-based crisis intervention protocols.
    """
    
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.detector = CrisisDetector()
    
    def respond(self, user_message: str, conversation_history: List[Dict], user_context: Dict) -> Dict:
        """
        Generate empathetic, clinically-informed response.
        
        Returns:
            {
                'message': str,
                'risk_assessment': Dict,
                'escalation_triggered': bool,
                'interventions': List[str],
                'next_action': str
            }
        """
        # Step 1: Assess risk
        risk = self.detector.detect_risk(user_message, conversation_history)
        
        # Step 2: Handle imminent danger
        if risk['risk_level'] == 'IMMINENT':
            return self._imminent_danger_response(risk, user_context)
        
        # Step 3: Generate response based on risk level
        if risk['risk_level'] == 'HIGH':
            response_type = 'high_risk'
        elif risk['risk_level'] == 'MEDIUM':
            response_type = 'medium_risk'
        else:
            response_type = 'supportive'
        
        # Step 4: Call Groq with crisis-aware prompt
        prompt = self._build_crisis_prompt(user_message, risk, response_type)
        
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    *conversation_history,
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            bot_message = completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq error: {e}")
            bot_message = self._fallback_response(risk['risk_level'])
        
        # Step 5: Attach interventions
        interventions = self._suggest_interventions(risk['risk_level'])
        
        return {
            'message': bot_message,
            'risk_assessment': risk,
            'escalation_triggered': risk['requires_escalation'],
            'interventions': interventions,
            'next_action': risk['recommended_action']
        }
    
    def _get_system_prompt(self) -> str:
        """System prompt for crisis counseling"""
        return """You are a compassionate mental health support assistant trained in crisis intervention.

CRITICAL GUIDELINES:
- Be warm, empathetic, and non-judgmental
- Validate the user's feelings
- Ask open-ended questions to understand their situation
- Provide evidence-based coping strategies (CBT, DBT, grounding)
- NEVER diagnose or prescribe medication
- ALWAYS encourage professional help for serious concerns
- Use simple, clear language
- Be culturally sensitive

If user expresses suicidal thoughts:
1. Take them seriously
2. Ask if they have a plan
3. Encourage immediate professional contact
4. Provide crisis hotline numbers
5. Stay engaged until they commit to safety

Remember: You are a support tool, not a replacement for professional care."""
    
    def _imminent_danger_response(self, risk: Dict, user_context: Dict) -> Dict:
        """Immediate intervention for imminent suicide risk"""
        country = user_context.get('country', 'US')
        resources = CrisisResources.get_resources(country)
        
        message = f"""I'm really concerned about your safety right now. 

🆘 **Please reach out for immediate help:**

📞 **Call: {resources['hotlines']['suicide_prevention']['number']}**
   ({resources['hotlines']['suicide_prevention']['name']})

🚨 **Emergency: {resources['hotlines']['emergency']['number']}**

You are not alone. Trained counselors are available 24/7. They've helped thousands of people in similar situations.

**I'm here with you.** Can you call one of these numbers right now? Or would you like me to help you find someone nearby?"""
        
        return {
            'message': message,
            'risk_assessment': risk,
            'escalation_triggered': True,
            'interventions': ['CRISIS_HOTLINE', 'EMERGENCY_CONTACT'],
            'next_action': 'URGENT_ESCALATION',
            'resources': resources
        }
    
    def _suggest_interventions(self, risk_level: str) -> List[str]:
        """Return appropriate coping interventions"""
        if risk_level == 'HIGH':
            return ['GROUNDING_5_4_3_2_1', 'BREATHING_BOX', 'CRISIS_HOTLINE']
        elif risk_level == 'MEDIUM':
            return ['BREATHING_4_7_8', 'POSITIVE_AFFIRMATIONS', 'JOURNALING']
        else:
            return ['MINDFULNESS', 'GRATITUDE', 'SELF_CARE']
