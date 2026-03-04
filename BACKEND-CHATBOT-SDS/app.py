from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from sentimentAnalysisService import sentiment_service

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# Enable CORS for API routes and permit the Authorization header
CORS(app, resources={r"/api/*": {"origins": "*"}},
    expose_headers=["Content-Type", "Authorization"],
    allow_headers=["Content-Type", "Authorization"])

# Configuration
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/sentiment_app')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Initialize extensions
mongo = PyMongo(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# Sentiment analysis service is initialized in sentimentAnalysisService.py

# Collections
try:
    users_collection = mongo.db.users
    chats_collection = mongo.db.chats
except AttributeError:
    # This usually happens if the MONGO_URI is missing the database name
    print("Error: MongoDB database not selected. Please ensure your MONGO_URI includes the database name.")
    print("Example: mongodb+srv://<user>:<password>@cluster.mongodb.net/<database_name>?retryWrites=true&w=majority")
    raise ValueError("MONGO_URI missing database name")




@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200


@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Check if user already exists
        if users_collection.find_one({'email': data['email']}):
            return jsonify({'error': 'Email already registered'}), 409
        
        if users_collection.find_one({'username': data['username']}):
            return jsonify({'error': 'Username already taken'}), 409
        
        # Hash password
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        # Create user
        user = {
            'username': data['username'],
            'email': data['email'],
            'password': hashed_password,
            'created_at': datetime.now(timezone.utc)
        }
        
        result = users_collection.insert_one(user)
        
        # Create access token
        access_token = create_access_token(identity=str(result.inserted_id))
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {
                'id': str(result.inserted_id),
                'username': data['username'],
                'email': data['email']
            }
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = users_collection.find_one({'email': data['email']})
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not bcrypt.check_password_hash(user['password'], data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user['_id']))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
@jwt_required()
def analyze():
    """Analyze sentiment of text"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate input
        if not data.get('text'):
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        analyzer = data.get('analyzer', 'hybrid')  # options: vader, hybrid, llm

        # Perform analysis based on chosen analyzer
        if analyzer == 'vader':
            sentiment_result = sentiment_service.analyze_sentiment(text, use_hybrid=False)
        elif analyzer == 'llm':
            sentiment_result = sentiment_service.analyze_sentiment(text, show_details=True, use_llm=True)
        else:
            sentiment_result = sentiment_service.analyze_sentiment(text)
        
        # Save to chat history
        chat_entry = {
            'user_id': current_user_id,
            'text': text,
            'sentiment': sentiment_result,
            'timestamp': datetime.now(timezone.utc)
        }
        
        chats_collection.insert_one(chat_entry)
        
        return jsonify({
            'text': text,
            'sentiment': sentiment_result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get user's chat history"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        skip = (page - 1) * limit
        
        # Get chat history
        chats = list(chats_collection.find(
            {'user_id': current_user_id}
        ).sort('timestamp', -1).skip(skip).limit(limit))
        
        # Convert ObjectId to string
        for chat in chats:
            chat['_id'] = str(chat['_id'])
            chat['timestamp'] = chat['timestamp'].isoformat()
        
        # Get total count
        total = chats_collection.count_documents({'user_id': current_user_id})
        
        return jsonify({
            'chats': chats,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history/<chat_id>', methods=['DELETE'])
@jwt_required()
def delete_chat(chat_id):
    """Delete a chat entry"""
    try:
        from bson.objectid import ObjectId
        current_user_id = get_jwt_identity()
        
        # Delete chat
        result = chats_collection.delete_one({
            '_id': ObjectId(chat_id),
            'user_id': current_user_id
        })
        
        if result.deleted_count == 0:
            return jsonify({'error': 'Chat not found'}), 404
        
        return jsonify({'message': 'Chat deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/user', methods=['GET'])
@jwt_required()
def get_user():
    """Get current user info"""
    try:
        from bson.objectid import ObjectId
        current_user_id = get_jwt_identity()
        
        user = users_collection.find_one({'_id': ObjectId(current_user_id)})
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': str(user['_id']),
            'username': user['username'],
            'email': user['email'],
            'created_at': user['created_at'].isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/test-samples', methods=['GET'])
def test_samples():
    """Test sentiment analysis with sample reviews
    
    This endpoint demonstrates VADER's capabilities and limitations.
    Useful for understanding how different text patterns are analyzed.
    """
    # Use the sentiment service for test samples
    return jsonify(sentiment_service.test_samples_analysis()), 200


@app.route('/api/analyze-detailed', methods=['POST'])
@jwt_required()
def analyze_detailed():
    """Analyze sentiment with detailed breakdown and insights"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('text'):
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        
        # Determine analyzer
        analyzer = data.get('analyzer', 'hybrid')
        if analyzer == 'vader':
            sentiment_result = sentiment_service.analyze_sentiment(text, show_details=True, use_hybrid=False)
        elif analyzer == 'llm':
            sentiment_result = sentiment_service.analyze_sentiment(text, show_details=True, use_llm=True)
        else:
            sentiment_result = sentiment_service.analyze_sentiment(text, show_details=True)
        
        # Add insights based on the analysis
        sentiment_result['insights'] = sentiment_service.generate_insights(sentiment_result)
        
        # Optionally save to history
        if data.get('save_to_history', True):
            chat_entry = {
                'user_id': current_user_id,
                'text': text,
                'sentiment': sentiment_result,
                'timestamp': datetime.now(timezone.utc)
            }
            chats_collection.insert_one(chat_entry)
        
        return jsonify({
            'text': text,
            'sentiment': sentiment_result
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare-analyzers', methods=['POST'])
@jwt_required()
def compare_analyzers():
    """Compare VADER-only vs Hybrid analysis side-by-side
    
    This endpoint is useful for understanding the differences between
    the two approaches and seeing which performs better for different texts.
    """
    try:
        data = request.get_json()
        
        if not data.get('text'):
            return jsonify({'error': 'Text is required'}), 400
        
        text = data['text']
        
        # Use the sentiment service for comparison
        include_llm = bool(data.get('include_llm', False))
        comparison = sentiment_service.compare_analyzers(text, show_details=True, include_llm=include_llm)
        
        return jsonify(comparison), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
