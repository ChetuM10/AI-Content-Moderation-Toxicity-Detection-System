"""
Toxicity Rewriting System - Hybrid Implementation
Groq API (Primary) + Enhanced Rule-Based (Fallback)
Ultra-fast professional text rewriting with comprehensive toxic word coverage
"""
from dotenv import load_dotenv
load_dotenv() 

from groq import Groq
import logging
import os
import re

logger = logging.getLogger(__name__)


# ============================================
# GROQ API REWRITER (PRIMARY) ⚡
# ============================================

class GroqRewriter:
    def __init__(self, api_key=None):
        """Initialize Groq with API key"""
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.client = None
        self.is_available = False

        if self.api_key and self.api_key != 'YOUR_API_KEY_HERE':
            try:
                self.client = Groq(api_key=self.api_key)

                # Test connection with minimal request
                test_response = self.client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=5
                )

                self.is_available = True
                logger.info("✅ Groq API initialized successfully")

            except Exception as e:
                logger.warning(f"⚠️ Groq initialization failed: {str(e)}")
                self.is_available = False

    def rewrite(self, toxic_text):
        """Rewrite toxic text using Groq API"""
        if not self.is_available:
            raise Exception("Groq API not available")

        try:
            prompt = f"""Rewrite this toxic feedback into professional, constructive language while preserving the core message. Remove all profanity, insults, and offensive language.

Original: "{toxic_text}"

Professional version (output ONLY the rewritten text):"""

            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.5
            )

            rewritten = response.choices[0].message.content.strip()
            rewritten = rewritten.strip('"\'')

            logger.info(f"✅ Groq rewrite successful")
            return rewritten

        except Exception as e:
            logger.error(f"❌ Groq rewrite failed: {str(e)}")
            raise


# ============================================
# ENHANCED RULE-BASED REWRITER (FALLBACK) 🔄
# ============================================

class RuleBasedRewriter:
    """Enhanced rule-based detoxification - FIXED version"""

    def __init__(self):
        self.is_available = True
        logger.info("✅ Rule-based rewriter initialized")

    def rewrite(self, toxic_text):
        """Rewrite toxic text using comprehensive rule-based approach"""
        try:
            result = self._comprehensive_detoxify(toxic_text)
            logger.info(f"✅ Rule-based rewrite successful")
            return result
        except Exception as e:
            logger.error(f"❌ Rule-based rewrite failed: {str(e)}")
            return toxic_text

    def _comprehensive_detoxify(self, text):
        """FIXED: Comprehensive toxic word replacement"""

        # UPDATED toxic word replacements - FIXED ISSUES
        toxic_replacements = {
            # Strong profanity - FIXED
            'fuck': 'very',
            'fucking': 'very',
            'fucked': 'flawed',
            'fck': 'very',
            'f*ck': 'very',
            'shit': 'poor',
            'shitty': 'subpar',
            'sh*t': 'poor',
            'damn': 'darn',  # FIXED: was empty, now has value
            'damned': 'unfortunate',
            'hell': 'heck',
            'ass': 'rear',  # FIXED: was empty
            'arse': 'rear',
            'asshole': 'person',  # Singular
            'assholes': 'people',  # FIXED: Added plural
            'bastard': 'person',
            'bastards': 'individuals',
            'bitch': 'person',
            'bitches': 'people',
            'piss': 'annoy',
            'pissed': 'frustrated',

            # Intelligence insults - COMPLETE
            'stupid': 'inexperienced',
            'idiot': 'individual',
            'idiots': 'team members',
            'moron': 'person',
            'morons': 'individuals',
            'dumb': 'uninformed',
            'dumbass': 'person',
            'fool': 'person',
            'fools': 'individuals',
            'retard': 'person',
            'retarded': 'limited',
            'imbecile': 'person',
            'dimwit': 'person',

            # Quality insults
            'garbage': 'substandard',
            'trash': 'inadequate',
            'crap': 'unsatisfactory',
            'crappy': 'poor quality',
            'rubbish': 'inadequate',
            'junk': 'subpar',
            'worthless': 'of limited value',
            'useless': 'ineffective',
            'pathetic': 'disappointing',
            'terrible': 'below expectations',
            'awful': 'concerning',
            'horrible': 'problematic',
            'horrendous': 'very poor',
            'abysmal': 'very poor',
            'worst': 'least effective',
            'lousy': 'poor',
            'crummy': 'inadequate',
            'disgusting': 'unpleasant',

            # Behavioral insults
            'lazy': 'unmotivated',
            'incompetent': 'inexperienced',
            'amateur': 'beginner',
            'joke': 'less serious',
            'clown': 'person',
            'clowns': 'individuals',
            'loser': 'person',
            'losers': 'individuals',

            # Verbs/actions
            'sucks': 'needs improvement',
            'sucking': 'performing poorly',
            'hate': 'dislike',
            'hating': 'disliking',
            'despise': 'dislike',
            'detest': 'dislike',
        }

        # Process text
        result = text

        # Replace toxic words using regex for whole words only
        for toxic, replacement in toxic_replacements.items():
            pattern = r'\b' + re.escape(toxic) + r'\b'
            result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

        # Clean up multiple spaces
        result = re.sub(r'\s+', ' ', result)
        result = result.strip()

        # Capitalize first letter
        if result:
            result = result[0].upper() + result[1:]

        # Add period if missing
        if result and result[-1] not in '.!?':
            result += '.'

        # Add professional framing for negative feedback
        negative_indicators = [
            'substandard', 'inadequate', 'disappointing', 'needs improvement',
            'inexperienced', 'below expectations', 'poor', 'subpar',
            'ineffective', 'concerning', 'problematic', 'limited',
            'uninformed', 'unmotivated', 'flawed', 'unpleasant'
        ]

        # Only add framing if it contains negative words
        if any(word in result.lower() for word in negative_indicators):
            professional_starters = [
                'i believe', 'in my opinion', 'it appears', 'from my perspective', 'this']
            if not any(result.lower().startswith(starter) for starter in professional_starters):
                result = "I believe " + result[0].lower() + result[1:]

        return result


# ============================================
# SMART ROUTER (HYBRID LOGIC) 🚀
# ============================================

class HybridRewriter:
    def __init__(self, api_key=None, groq_api_key=None, prefer_local=False):
        """
        Initialize hybrid rewriter with Groq and Rule-based fallback

        Args:
            groq_api_key (str): Groq API key
            prefer_local (bool): Use rule-based method (default: False to use Groq)
        """
        self.groq = GroqRewriter(api_key or groq_api_key)
        self.rule_based = RuleBasedRewriter()
        self.prefer_local = prefer_local

        logger.info("🚀 Hybrid Rewriter initialized")
        logger.info(
            f"   - Groq API: {'✅ Ready' if self.groq.is_available else '❌ Unavailable'}")
        logger.info(f"   - Rule-based: ✅ Ready")
        logger.info(f"   - Prefer Local: {prefer_local}")

    def rewrite(self, toxic_text):
        """
        Intelligently rewrite toxic text using best available method

        Priority:
        1. Groq API (if available and prefer_local=False)
        2. Rule-based (fallback or if prefer_local=True)
        """
        result = {
            'rewritten_text': toxic_text,
            'method_used': 'none',
            'success': False,
            'error': None
        }

        # Try Groq first ONLY if prefer_local is False AND Groq is available
        if not self.prefer_local and self.groq.is_available:
            try:
                result['rewritten_text'] = self.groq.rewrite(toxic_text)
                result['method_used'] = 'groq'
                result['success'] = True
                return result
            except Exception as e:
                logger.warning(f"⚠️ Groq failed, trying rule-based fallback")
                result['error'] = str(e)

        # Use rule-based rewriter as fallback
        try:
            result['rewritten_text'] = self.rule_based.rewrite(toxic_text)
            result['method_used'] = 'rules'
            result['success'] = True
            return result
        except Exception as e:
            logger.error(f"❌ All rewriting methods failed: {str(e)}")
            result['error'] = f"All methods failed: {str(e)}"
            result['method_used'] = 'failed'
            return result


# ============================================
# CONVENIENCE FUNCTION 🎯
# ============================================

def rewrite_toxic_text(text, api_key=None, prefer_local=False):
    """Quick function to rewrite toxic text"""
    rewriter = HybridRewriter(api_key, prefer_local)
    return rewriter.rewrite(text)


# ============================================
# TESTING 🧪
# ============================================

if __name__ == "__main__":
    print("="*70)
    print("TESTING HYBRID REWRITER")
    print("="*70)

    test_cases = [
        "don't give a damn about quality",
        "brain-dead assholes developed this",
        "This is fucking garbage shit",
        "You stupid idiots made this crap"
    ]

    API_KEY = os.getenv('GROQ_API_KEY', 'YOUR_API_KEY_HERE')

    for test_text in test_cases:
        print(f"\n📝 Original: {test_text}")
        result = rewrite_toxic_text(
            test_text, api_key=API_KEY, prefer_local=False)
        print(f"✨ Rewritten: {result['rewritten_text']}")
        print(f"🔧 Method: {result['method_used']}")
        print("-" * 70)
