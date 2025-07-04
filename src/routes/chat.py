# Simplified chat.py for debugging
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat_test():
    # Get the user's message just to confirm it's being received
    data = request.get_json()
    user_message = data.get('message', 'No message received')

    # Print to the Render logs to prove this function was called
    print(f"TEST: /api/chat endpoint was hit! Received message: '{user_message}'")

    # Immediately return a hardcoded success response
    test_response = {
        "message": "TEST successful! The chat widget is connected to the backend.",
        "type": "greeting"
    }

    return jsonify({'success': True, 'response': test_response})