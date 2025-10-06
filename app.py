"""
Toxicity Detection & Sentiment Analysis System with AI Rewriting
Complete Flask Application with Groq + Rule-Based Hybrid Rewriter
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from detoxify import Detoxify
from textblob import TextBlob
from dotenv import load_dotenv
import os
import logging
import re
from datetime import datetime

# Import our hybrid rewriter
from rewriter import HybridRewriter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024  # 16 KB max request size
app.config['JSON_SORT_KEYS'] = False

# Global model variables
model = None
rewriter = None

# Comprehensive toxic words list
TOXIC_WORDS = [
    'bastard', 'worthless', 'garbage', 'stupid', 'idiot', 'hate',
    'hurt', 'kill', 'damn', 'hell', 'ass', 'crap', 'suck', 'ugly',
    'dumb', 'fool', 'moron', 'loser', 'jerk', 'screw', 'shit',
    'fuck', 'bitch', 'dick', 'piss', 'fag', 'retard', 'slut',
    'whore', 'douche', 'asshole', 'assholes', 'dumbass', 'fatass'
]


def load_model():
    """Load Detoxify model with error handling"""
    global model
    try:
        logger.info("🔄 Loading Detoxify model...")
        model = Detoxify('unbiased')
        logger.info("✅ Detoxify model loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load Detoxify model: {str(e)}")
        return False


def load_rewriter():
    """Load Hybrid Rewriter (Groq + Rules)"""
    global rewriter
    try:
        logger.info("🔄 Initializing Hybrid Rewriter...")
        api_key = os.getenv('GROQ_API_KEY')
        prefer_local = os.getenv('PREFER_LOCAL', 'False').lower() == 'true'

        rewriter = HybridRewriter(
            groq_api_key=api_key,
            prefer_local=prefer_local
        )
        logger.info("✅ Hybrid Rewriter initialized!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load rewriter: {str(e)}")
        return False


def analyze_sentiment(text):
    """Analyze sentiment using TextBlob"""
    try:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 (negative) to 1 (positive)
        # 0 (objective) to 1 (subjective)
        subjectivity = blob.sentiment.subjectivity

        # Determine sentiment label and emoji
        if polarity > 0.1:
            label = "Positive"
            emoji = "😊"
            color = "#28a745"
        elif polarity < -0.1:
            label = "Negative"
            emoji = "😞"
            color = "#dc3545"
        else:
            label = "Neutral"
            emoji = "😐"
            color = "#6c757d"

        # Calculate confidence as percentage
        confidence = abs(polarity) * 100

        return {
            'label': label,
            'emoji': emoji,
            'color': color,
            'polarity': round(polarity, 4),
            'subjectivity': round(subjectivity, 4),
            'confidence': round(confidence, 2),
            'score': round((polarity + 1) / 2, 4)  # Normalize to 0-1
        }
    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}")
        return {
            'label': 'Unknown',
            'emoji': '❓',
            'color': '#6c757d',
            'polarity': 0.0,
            'subjectivity': 0.0,
            'confidence': 0.0,
            'score': 0.5,
            'error': str(e)
        }


def clean_toxic_text(text, toxic_words=None):
    """Clean toxic words from text with case-insensitive matching"""
    if toxic_words is None:
        toxic_words = TOXIC_WORDS

    cleaned_text = text
    toxic_words_found = []

    for word in toxic_words:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        if pattern.search(cleaned_text):
            toxic_words_found.append(word)
            cleaned_text = pattern.sub('[REDACTED]', cleaned_text)

    return cleaned_text, toxic_words_found


def validate_input(text):
    """Validate input text"""
    if not text:
        return False, "Text cannot be empty"

    if not isinstance(text, str):
        return False, "Text must be a string"

    if len(text.strip()) == 0:
        return False, "Text cannot contain only whitespace"

    if len(text) > 5000:
        return False, "Text exceeds maximum length of 5000 characters"

    if len(text) < 3:
        return False, "Text must be at least 3 characters long"

    return True, None


@app.route('/')
def home():
    """Serve the main HTML page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        return jsonify({'error': 'Template not found. Please ensure index.html exists in templates/ folder'}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'detoxify_loaded': model is not None,
        'rewriter_loaded': rewriter is not None,
        'groq_available': rewriter.groq.is_available if rewriter else False,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Main analysis endpoint for toxicity detection and sentiment analysis"""
    try:
        # Check if model is loaded
        if model is None:
            return jsonify({'error': 'Model not loaded. Please restart the server.'}), 503

        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400

        # Extract text
        text = data.get('text', '')

        # Validate input
        is_valid, error_msg = validate_input(text)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        # Get toxicity predictions
        logger.info(f"Analyzing text of length: {len(text)}")
        tox_results = model.predict(text)

        # Convert numpy to float
        tox_scores = {k: float(v) for k, v in tox_results.items()}

        # Determine if toxic (threshold: 0.7)
        is_toxic = tox_scores['toxicity'] > 0.7

        # Clean text if toxic
        cleaned_text = text
        toxic_words_found = []

        if is_toxic:
            cleaned_text, toxic_words_found = clean_toxic_text(
                text, TOXIC_WORDS)

        # Analyze sentiment on BOTH original and cleaned text
        sentiment_original = analyze_sentiment(text)
        sentiment_cleaned = analyze_sentiment(cleaned_text)

        # Calculate sentiment improvement
        sentiment_improvement = sentiment_cleaned['polarity'] - \
            sentiment_original['polarity']

        # FIXED LOGIC: Only show improvement if cleaned sentiment is Positive or Neutral
        sentiment_improved = (
            sentiment_improvement > 0.1 and
            sentiment_cleaned['label'] in ['Positive', 'Neutral']
        )

        # Get flagged categories (threshold: 0.7)
        flagged = [k for k, v in tox_scores.items() if v > 0.7]

        # AI-powered rewriting suggestion
        rewritten_suggestion = None
        rewrite_method = None

        if is_toxic and rewriter is not None:
            try:
                logger.info("🤖 Generating AI rewrite suggestion...")
                rewrite_result = rewriter.rewrite(text)
                if rewrite_result['success']:
                    rewritten_suggestion = rewrite_result['rewritten_text']
                    rewrite_method = rewrite_result['method_used']
                    logger.info(f"✅ Rewrite successful using {rewrite_method}")
            except Exception as e:
                logger.error(f"Rewrite failed: {str(e)}")

        # Prepare response
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'original_text': text,
            'cleaned_text': cleaned_text,
            'rewrite_suggestion': rewritten_suggestion,
            'rewrite_method': rewrite_method,
            'text_length': len(text),
            'is_toxic': is_toxic,
            'toxicity_scores': tox_scores,
            'categories_flagged': flagged,
            'toxic_words_found': list(set(toxic_words_found)),
            'toxic_word_count': len(toxic_words_found),
            'overall_toxicity': round(tox_scores['toxicity'] * 100, 2),
            'sentiment_original': sentiment_original,
            'sentiment_cleaned': sentiment_cleaned,
            'sentiment_improvement': round(sentiment_improvement, 4),
            'sentiment_improved': sentiment_improved
        }

        logger.info(
            f"Analysis complete - Toxic: {is_toxic}, Sentiment: {sentiment_cleaned['label']}, Method: {rewrite_method}")
        return jsonify(response)

    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Analysis failed: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/rewrite', methods=['POST'])
def rewrite_text():
    """AI-powered text rewriting endpoint"""
    try:
        if rewriter is None:
            return jsonify({'error': 'Rewriter not loaded'}), 503

        data = request.get_json()
        text = data.get('text', '')

        # Validate input
        is_valid, error_msg = validate_input(text)
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        # Rewrite text
        logger.info(f"Rewriting text: {text[:50]}...")
        result = rewriter.rewrite(text)

        return jsonify({
            'success': result['success'],
            'original_text': text,
            'rewritten_text': result['rewritten_text'],
            'method_used': result['method_used'],
            'error': result.get('error'),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Rewrite error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    return jsonify({
        'toxic_words_count': len(TOXIC_WORDS),
        'supported_categories': [
            'toxicity',
            'severe_toxicity',
            'obscene',
            'threat',
            'insult',
            'identity_attack',
            'sexual_explicit'
        ],
        'max_text_length': 5000,
        'sentiment_labels': ['Positive', 'Negative', 'Neutral'],
        'rewriter_available': rewriter is not None,
        'groq_available': rewriter.groq.is_available if rewriter else False
    })


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500


# Initialize models on startup
if __name__ == '__main__':
    print("="*70)
    print("🛡️  TOXICITY DETECTION & AI REWRITING SYSTEM")
    print("="*70)

    # Load Detoxify model
    detoxify_loaded = load_model()

    # Load Rewriter (Groq + Rules)
    rewriter_loaded = load_rewriter()

    if detoxify_loaded:
        print("\n✅ Server ready!")
        print("🌐 Access: http://localhost:5000")
        print("📊 Health check: http://localhost:5000/api/health")
        print("📈 Stats: http://localhost:5000/api/stats")

        if rewriter_loaded:
            groq_status = "✅ Ready" if (
                rewriter and rewriter.groq.is_available) else "⚠️  Fallback to Rules"
            print(f"🤖 AI Rewriter: {groq_status}")
        else:
            print("🤖 AI Rewriter: ⚠️  Not available (check .env file)")

        print("\n" + "="*70 + "\n")

        # Run Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Prevent model reloading
        )
    else:
        print("\n❌ Failed to start server - Model loading failed")
        print("Please check if detoxify is installed correctly")
        print("Run: pip install detoxify transformers torch textblob flask flask-cors python-dotenv groq")
