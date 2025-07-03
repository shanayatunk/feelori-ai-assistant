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
        return {"message": "Sorry, my product knowledge is still being trained.", "type": "error"}

    product_catalog = knowledge_base.get('product_catalog', {})
    price_limit = extract_price_limit(message)
    keywords = extract_keywords(message)

    # Match specific product titles or descriptions
    matches = []
    for product in product_catalog.values():
        title = product['title'].lower()
        tags = product.get('tags', '').lower()
        if any(k in title or k in tags for k in keywords):
            if price_limit is None or float(product['price']) <= price_limit:
                matches.append(product)

    if matches:
        return {
            "message": f"Here are {len(matches)} product(s) I found for your request:",
            "type": "product_recommendation",
            "products": matches[:3]
        }

    # FAQ fallback
    faq = knowledge_base.get('faq_responses', {})
    if any(k in message_lower for k in ['shipping', 'delivery']):
        return {"message": faq.get('shipping_info', "We offer standard shipping within 3–5 days."), "type": "faq"}
    if any(k in message_lower for k in ['return', 'refund']):
        return {"message": faq.get('return_policy', "Returns accepted within 30 days of purchase."), "type": "faq"}
    if any(k in message_lower for k in ['care', 'wash']):
        return {"message": faq.get('product_care', "Most items can be wiped clean with a soft cloth."), "type": "faq"}

    # Greeting
    if any(k in message_lower for k in ['hello', 'hi', 'hey']):
        return {"message": "Hello! Welcome to FeelOri ✨ What are you looking for today?", "type": "greeting"}

    # Help intent
    if any(k in message_lower for k in ['help', 'assist']):
        return {"message": "I'm here to help you browse products, check delivery info, or suggest the right jewelry/hair items.", "type": "help"}

    # Default fallback
    return {
        "message": "I'm not sure I understood. Could you tell me what kind of product you're looking for or your price range?",
        "type": "general"
    }


@chat_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        if not message:
            return jsonify({'error': 'Message is required'}), 400

        response = get_ai_response(message)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/chat/quick-action', methods=['POST'])
@cross_origin()
def quick_action():
    try:
        data = request.get_json()
        action = data.get('action', '')

        if action == 'show_products':
            response = get_ai_response('show products')
        elif action == 'shipping_info':
            response = get_ai_response('shipping')
        elif action == 'return_policy':
            response = get_ai_response('return')
        elif action == 'product_care':
            response = get_ai_response('care')
        else:
            response = {"message": "Not sure how to help with that. Can you rephrase?", "type": "general"}

        return jsonify({'success': True, 'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
