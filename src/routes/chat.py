from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import re
from src.services import training_service

chat_bp = Blueprint('chat', __name__)

def get_ai_response(message):
    knowledge_base = training_service.get_knowledge_base()
    if not knowledge_base or not knowledge_base.get('product_catalog'):
        return {"message": "Sorry, my product knowledge is still being trained. Please use the admin dashboard to process products.", "type": "error"}

    message_lower = message.lower()
    product_catalog = knowledge_base.get('product_catalog', {})
    
    # --- START OF PRICE FILTER FIX ---
    # This new logic correctly understands "under 2000", "below 500", etc.
    price_match = re.search(r'(?:under|below|less than)\s*(\d+)', message_lower)
    if price_match:
        price_limit = int(price_match.group(1))
        
        filtered_products = [
            p for p in product_catalog.values()
            if p.get('price') and float(p['price']) <= price_limit
        ]
        
        if filtered_products:
            return {
                "message": f"Here are {len(filtered_products)} product(s) I found for you under ₹{price_limit}:",
                "type": "product_recommendation",
                "products": filtered_products[:3] # Show up to 3 products
            }
        else:
            return {
                "message": f"Sorry, I couldn't find any products below ₹{price_limit}.",
                "type": "error"
            }
    # --- END OF PRICE FILTER FIX ---

    # --- Improved Product Search & FAQ Logic ---
    product_keywords = ['product', 'show', 'find', 'necklace', 'earring', 'studs', 'tops', 'set']
    if any(key in message_lower for key in product_keywords):
        keywords = [w for w in re.findall(r'\b\w+\b', message_lower) if len(w) > 3]
        matches = []
        for product in product_catalog.values():
            title = product.get('title', '').lower()
            tags_data = product.get('tags', [])
            tags = ', '.join(tags_data).lower() if isinstance(tags_data, list) else str(tags_data).lower()
            if any(k in title or k in tags for k in keywords):
                matches.append(product)
        
        if matches:
            return {"message": "Here are some products that match your request:", "type": "product_recommendation", "products": matches[:3]}

    faq_responses = knowledge_base.get('faq_responses', {})
    if 'shipping' in message_lower or 'delivery' in message_lower:
        return {"message": faq_responses.get('shipping_info'), "type": "faq"}
    if 'return' in message_lower or 'refund' in message_lower:
        return {"message": faq_responses.get('return_policy'), "type": "faq"}
    if 'care' in message_lower or 'wash' in message_lower:
        return {"message": faq_responses.get('product_care'), "type": "faq"}

    # Greeting check
    if any(k in message_lower for k in ['hello', 'hi', 'hey']):
        return {"message": "Hello! Welcome to FeelOri ✨ What are you looking for today?", "type": "greeting"}

    # Default fallback
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