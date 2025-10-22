"""
Toxicity Detection & Sentiment Analysis System with AI Rewriting
Complete Flask Application with Groq + Rule-Based Hybrid Rewriter + File Upload
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from pymongo.errors import PyMongoError
from detoxify import Detoxify
from textblob import TextBlob
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import PyPDF2
import io
import os
import logging
import re
from datetime import datetime
from typing import Any, Dict, List
from bson import ObjectId
from bson.errors import InvalidId

# Import our hybrid rewriter
from rewriter import HybridRewriter
from src.auth.routes import create_auth_blueprint
from src.db.client import get_collection
from src.db.models import AnalysisRecord
from src.history.routes import create_history_blueprint

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
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max
app.config['JSON_SORT_KEYS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'change-me')
app.config['JWT_TOKEN_LOCATION'] = ['headers']

jwt = JWTManager(app)

# Database configuration
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'senti_clean')

users_collection = get_collection(MONGO_URI, MONGO_DB_NAME, 'users')
history_collection = get_collection(
    MONGO_URI, MONGO_DB_NAME, 'analysis_history')

# Register blueprints
app.register_blueprint(create_auth_blueprint(users_collection))
app.register_blueprint(create_history_blueprint(history_collection))

# File upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Global model variables
model = None
rewriter = None


def _get_authenticated_user_id() -> ObjectId:
    """Return the authenticated user's ObjectId."""
    identity = get_jwt_identity()
    if not identity:
        raise ValueError("Authentication required.")
    try:
        return ObjectId(identity)
    except (InvalidId, TypeError) as exc:
        raise ValueError("Invalid user identity.") from exc


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


# Ensure core components are loaded even when running via `flask run`
detoxify_loaded = load_model()
rewriter_loaded = load_rewriter()


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
@jwt_required(optional=True)
def analyze():
    """Main analysis endpoint for toxicity detection and sentiment analysis"""
    try:
        # Check if model is loaded
        if model is None:
            return jsonify({'error': 'Model not loaded. Please restart the server.'}), 503

        # Handle optional authentication
        try:
            user_id = _get_authenticated_user_id()
            authenticated = True
        except (ValueError, Exception):
            user_id = None
            authenticated = False
            logger.info("Anonymous analysis request")

        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided', 'record_id': None}), 400

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
        toxic_words_found: List[str] = []

        if is_toxic:
            cleaned_text, toxic_words_found = clean_toxic_text(
                text, TOXIC_WORDS)

        unique_toxic_words = sorted(set(toxic_words_found))

        # Analyze sentiment on BOTH original and cleaned text
        sentiment_original = analyze_sentiment(text)
        sentiment_cleaned = analyze_sentiment(cleaned_text)

        # Calculate sentiment improvement
        sentiment_improvement = sentiment_cleaned['polarity'] - \
            sentiment_original['polarity']

        # Only show improvement if cleaned sentiment is Positive or Neutral
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

        # Persist analysis history (only if authenticated)
        record_id = None
        if authenticated and user_id:
            try:
                history_document = AnalysisRecord(
                    user_id=user_id,
                    original_text=text,
                    cleaned_text=cleaned_text,
                    rewrite_suggestion=rewritten_suggestion,
                    rewrite_method=rewrite_method,
                    toxicity_scores=tox_scores,
                    sentiment_original=sentiment_original,
                    sentiment_cleaned=sentiment_cleaned,
                    categories_flagged=flagged,
                    toxic_words_found=unique_toxic_words,
                    toxic_word_count=len(unique_toxic_words),
                    overall_toxicity=round(tox_scores['toxicity'] * 100, 2),
                    sentiment_improvement=round(sentiment_improvement, 4),
                    sentiment_improved=sentiment_improved,
                    is_toxic=is_toxic,
                    source='text',
                    metadata={},
                ).to_document()

                insert_result = history_collection.insert_one(history_document)
                record_id = str(insert_result.inserted_id)
            except PyMongoError as db_error:
                logger.error(
                    f"Failed to persist analysis history: {db_error}", exc_info=True)

        # Prepare response
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'record_id': record_id,
            'original_text': text,
            'cleaned_text': cleaned_text,
            'rewrite_suggestion': rewritten_suggestion,
            'rewrite_method': rewrite_method,
            'text_length': len(text),
            'is_toxic': is_toxic,
            'toxicity_scores': tox_scores,
            'categories_flagged': flagged,
            'toxic_words_found': unique_toxic_words,
            'toxic_word_count': len(unique_toxic_words),
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


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """File upload endpoint for batch analysis"""
    try:
        # Check if model is loaded
        if model is None:
            return jsonify({'error': 'Model not loaded. Please restart the server.'}), 503

        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Only .txt and .pdf files allowed'}), 400

        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()

        # Extract text based on file type
        text_content = ""

        if file_ext == 'txt':
            text_content = file.read().decode('utf-8')

        elif file_ext == 'pdf':
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"

        # Split into lines and filter empty ones
        lines = [line.strip()
                 for line in text_content.split('\n') if line.strip()]

        if not lines:
            return jsonify({'error': 'No text found in file'}), 400

        # Analyze each line
        results = []
        for idx, line in enumerate(lines, 1):
            if len(line) < 3:  # Skip very short lines
                continue

            # Use existing model to analyze
            analysis = model.predict(line)
            toxicity_score = float(analysis['toxicity'])
            is_toxic = toxicity_score > 0.7

            results.append({
                'line_number': idx,
                'text': line[:100] + '...' if len(line) > 100 else line,
                'full_text': line,
                'toxicity_score': round(toxicity_score, 3),
                'is_toxic': is_toxic,
                'categories': {k: round(float(v), 3) for k, v in analysis.items()}
            })

        logger.info(
            f"File upload analysis complete: {len(results)} lines analyzed")

        return jsonify({
            'success': True,
            'filename': filename,
            'total_lines': len(lines),
            'analyzed_lines': len(results),
            'toxic_count': sum(1 for r in results if r['is_toxic']),
            'safe_count': sum(1 for r in results if not r['is_toxic']),
            'results': results,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"File upload error: {str(e)}", exc_info=True)
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
        'max_file_size': '16 MB',
        'supported_file_types': list(ALLOWED_EXTENSIONS),
        'sentiment_labels': ['Positive', 'Negative', 'Neutral'],
        'rewriter_available': rewriter is not None,
        'groq_available': rewriter.groq.is_available if rewriter else False
    })


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(413)
def request_entity_too_large(e):
    """Handle file too large errors"""
    return jsonify({'error': 'File too large. Maximum size is 16 MB'}), 413


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
        print("📁 File Upload: Supports .txt and .pdf (max 16 MB)")

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
        print("Run: pip install detoxify transformers torch textblob flask flask-cors python-dotenv groq PyPDF2 flask-jwt-extended pymongo")
