from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.services.product_training import ProductTrainingService
import re

chat_bp = Blueprint('chat', __name__)
training_service = ProductTrainingService()

def extract_price_limit(message):
    matches = re.findall(r'(?:under|below|less than)\s*(?:₹|rs\.?|rupees)?\s*(\d+)', message.lower())
    return int(matches[0]) if matches else None

def extract_keywords(message):
    return [w for w in re.findall(r'\b\w+\b', message.lower()) if len(w) > 3]

def get_ai_response(message, conversation_history=None):
    message_lower = message.lower()
    knowledge_base = training_service.load_knowledge_base()
    if not knowledge_base:
        return {"message": "Sorry, my product knowledge is still being trained. Please ask the administrator to process the products.", "type": "error"}

    product_catalog = knowledge_base.get('product_catalog', {})
    price_limit = extract_price_limit(message)
    keywords = extract_keywords(message)

    matches = []
    if product_catalog:
        for product in product_catalog.values():
            title = product.get('title', '').lower()
            
            # --- START OF THE FIX ---
            # Safely handle product tags, whether they are a string or a list
            tags_data = product.get('tags', '')
            if isinstance(tags_data, list):
                tags = ', '.join(tags_data).lower()
            else:
                tags = str(tags_data).lower()
            # --- END OF THE FIX ---
            
            if any(k in title or k in tags for k in keywords):
                product_price = product.get('price')
                if price_limit is None or (product_price and float(product_price) <= price_limit):
                    matches.append(product)

    if matches:
        return {
            "message": f"I found {len(matches)} product(s) you might like:",
            "type": "product_recommendation",
            "products": matches[:3]
        }

    faq = knowledge_base.get('faq_responses', {})
    if any(k in message_lower for k in ['shipping', 'delivery']):
        return {"message": faq.get('shipping_info', "We offer standard shipping within 3–5 business days."), "type": "faq"}
    if any(k in message_lower for k in ['return', 'refund']):
        return {"message": faq.get('return_policy', "We accept returns within 30 days of purchase."), "type": "faq"}
    if any(k in message_lower for k in ['care', 'wash']):
        return {"message": faq.get('product_care', "Most items can be wiped clean with a soft, damp cloth."), "type": "faq"}

    if any(k in message_lower for k in ['hello', 'hi', 'hey']):
        return {"message": "Hello! Welcome to FeelOri ✨ What are you looking for today?", "type": "greeting"}

    if any(k in message_lower for k in ['help', 'assist']):
        return {"message": "I can help you find products, check shipping info, or answer questions about our return policy.", "type": "help"}

    return {
        "message": "I'm not sure I understood. Could you tell me more about what you're looking for?",
        "type": "general"
    }

@chat_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required in request body'}), 400
        
        message = data.get('message', '')
        response = get_ai_response(message)
        return jsonify({'success': True, 'response': response})

    except Exception as e:
        print(f"CRITICAL ERROR in /chat endpoint: {str(e)}")
        return jsonify({'error': 'An unexpected internal server error occurred.'}), 500