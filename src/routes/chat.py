# src/routes/chat.py
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import re
from src.services import training_service

chat_bp = Blueprint('chat', __name__)

def get_ai_response(message):
    knowledge_base = training_service.get_knowledge_base()
    if not knowledge_base.get('product_catalog'):
        return {"message": "Sorry, my product knowledge is still being trained. Please use the admin dashboard to process products.", "type": "error"}

    message_lower = message.lower()
    product_catalog = knowledge_base.get('product_catalog', {})
    
    # FAQ check
    faq_responses = knowledge_base.get('faq_responses', {})
    for topic, response in faq_responses.items():
        keywords = topic.replace('_info', '').split('_')
        if any(key in message_lower for key in keywords):
            return {"message": response, "type": "faq"}

    # Greeting check
    if any(k in message_lower for k in ['hello', 'hi', 'hey']):
        return {"message": "Hello! Welcome to FeelOri ✨ What are you looking for today?", "type": "greeting"}

    # Product search logic
    keywords = [w for w in re.findall(r'\b\w+\b', message_lower) if len(w) > 3]
    matches = []
    for product in product_catalog.values():
        title = product.get('title', '').lower()
        tags_data = product.get('tags', [])
        tags = ', '.join(tags_data).lower() if isinstance(tags_data, list) else str(tags_data).lower()
        if any(k in title or k in tags for k in keywords):
            matches.append(product)

    if matches:
        return {"message": f"I found {len(matches)} product(s) you might like:", "type": "product_recommendation", "products": matches[:3]}

    return {"message": "I'm not sure I understood. Could you tell me more about what you're looking for?", "type": "general"}

@chat_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        response = get_ai_response(message)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        print(f"Error in /chat: {str(e)}")
        return jsonify({'error': 'An internal server error occurred.'}), 500