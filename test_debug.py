from dotenv import load_dotenv
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env
load_dotenv()

# Check environment
api_key = os.getenv('GROQ_API_KEY')
print(f"1. API Key loaded: {api_key[:20] if api_key else 'NONE'}...")
print(f"2. API Key length: {len(api_key) if api_key else 0}")
print(f"3. Prefer Local: {os.getenv('PREFER_LOCAL')}")

# Try importing
try:
    from groq import Groq
    print("4. ✅ Groq module imported")
    
    # Try creating client
    client = Groq(api_key=api_key)
    print("5. ✅ Groq client created")
    
    # Try API call
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": "hi"}],
        max_tokens=10
    )
    print(f"6. ✅ API WORKS! Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

# Now try rewriter
print("\n" + "="*50)
print("Testing rewriter.py import:")
try:
    from rewriter import HybridRewriter
    print("7. ✅ Rewriter imported")
    
    rewriter = HybridRewriter(api_key=api_key, prefer_local=False)
    print(f"8. Groq available: {rewriter.groq.is_available}")
    
    result = rewriter.rewrite("This is shit")
    print(f"9. Method used: {result['method_used']}")
    print(f"10. Result: {result['rewritten_text']}")
    
except Exception as e:
    print(f"❌ Rewriter ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
