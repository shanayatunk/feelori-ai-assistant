from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import json
from src.services.product_training import ProductTrainingService

chat_bp = Blueprint('chat', __name__)

# Initialize training service for knowledge base access
training_service = ProductTrainingService()

def get_ai_response(message, conversation_history=None):
    """Generate AI response using trained knowledge base"""
    message_lower = message.lower()
    
    # Load knowledge base
    knowledge_base = training_service.load_knowledge_base()
    
    # Check for product search queries
    if any(keyword in message_lower for keyword in ['looking for', 'need', 'want', 'find', 'recommend']):
        # Extract product-related keywords
        product_keywords = []
        for word in message.split():
            if len(word) > 3:  # Skip short words
                product_keywords.append(word.lower())
        
        # Search for products
        search_query = ' '.join(product_keywords)
        search_results = training_service.search_products(search_query, limit=3)
        
        if search_results:
            response = {
                "message": "I found some great products for you:",
                "type": "product_recommendation",
                "products": search_results
            }
            return response
    
    # Check for specific product categories
    category_keywords = {
        'pillow': 'sleep',
        'sleep': 'sleep',
        'comfort': 'comfort',
        'wellness': 'wellness',
        'aromatherapy': 'wellness',
        'diffuser': 'wellness',
        'budget': 'budget',
        'cheap': 'budget',
        'premium': 'premium',
        'expensive': 'premium'
    }
    
    for keyword, category in category_keywords.items():
        if keyword in message_lower:
            recommendations = training_service.get_recommendations(category, limit=2)
            if recommendations:
                return {
                    "message": f"For {keyword}-related products, I recommend:",
                    "type": "product_recommendation",
                    "products": recommendations
                }
    
    # Check for FAQ-type questions
    faq_responses = knowledge_base.get('faq_responses', {}) if knowledge_base else {}
    
    if any(keyword in message_lower for keyword in ['shipping', 'delivery', 'ship']):
        return {
            "message": faq_responses.get('shipping_info', "We offer free shipping on orders over $50. Standard shipping takes 3-5 business days."),
            "type": "faq"
        }
    
    if any(keyword in message_lower for keyword in ['return', 'refund', 'exchange']):
        return {
            "message": faq_responses.get('return_policy', "We have a 30-day return policy. Items must be in original condition with tags attached."),
            "type": "faq"
        }
    
    if any(keyword in message_lower for keyword in ['care', 'wash', 'clean', 'maintenance']):
        return {
            "message": faq_responses.get('product_care', "Care instructions vary by product. Most fabric items are machine washable on gentle cycle."),
            "type": "faq"
        }
    
    if any(keyword in message_lower for keyword in ['warranty', 'guarantee']):
        return {
            "message": faq_responses.get('warranty', "All products come with a 1-year manufacturer warranty covering defects in materials and workmanship."),
            "type": "faq"
        }
    
    # Check for price-related queries
    if any(keyword in message_lower for keyword in ['price', 'cost', 'how much']):
        if knowledge_base and 'price_ranges' in knowledge_base:
            price_ranges = knowledge_base['price_ranges']
            response_text = "Here are our price ranges by category:\n\n"
            for category, ranges in price_ranges.items():
                response_text += f"**{category}**: ${ranges['min']:.2f} - ${ranges['max']:.2f} (avg: ${ranges['avg']:.2f})\n"
            return {
                "message": response_text,
                "type": "price_info"
            }
    
    # Check for product features
    if any(keyword in message_lower for keyword in ['features', 'benefits', 'what does', 'tell me about']):
        # Try to find specific product mentions
        if knowledge_base and 'product_catalog' in knowledge_base:
            products = knowledge_base['product_catalog']
            for product_id, product_info in products.items():
                if any(word in product_info['title'].lower() for word in message_lower.split()):
                    features = product_info.get('features', [])
                    if features:
                        return {
                            "message": f"The {product_info['title']} features: {', '.join(features)}. {product_info['summary']}",
                            "type": "product_info",
                            "product": {
                                "id": product_id,
                                "title": product_info['title'],
                                "summary": product_info['summary'],
                                "price": product_info['price'],
                                "features": features
                            }
                        }
    
    # Product listing
    if any(keyword in message_lower for keyword in ['products', 'catalog', 'what do you sell', 'browse', 'show products']):
        recommendations = training_service.get_recommendations('comfort', limit=3)
        if recommendations:
            return {
                "message": "Here are our featured products:",
                "type": "product_list",
                "products": recommendations
            }
    
    # Default responses based on context
    greeting_keywords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
    if any(keyword in message_lower for keyword in greeting_keywords):
        return {
            "message": "Hello! Welcome to Feelori! I'm here to help you find the perfect products for comfort and wellness. What can I assist you with today?",
            "type": "greeting"
        }
    
    if any(keyword in message_lower for keyword in ['help', 'assist', 'support']):
        return {
            "message": "I'm here to help! I can assist you with:\n• Finding products that match your needs\n• Answering questions about shipping and returns\n• Providing product recommendations\n• Explaining product features and benefits\n\nWhat would you like to know?",
            "type": "help"
        }
    
    if any(keyword in message_lower for keyword in ['thank', 'thanks']):
        return {
            "message": "You're welcome! Is there anything else I can help you with today?",
            "type": "acknowledgment"
        }
    
    # Default response
    return {
        "message": "I'd be happy to help you find the perfect products! Could you tell me more about what you're looking for? For example, are you interested in sleep products, wellness items, or something specific for comfort?",
        "type": "general"
    }

@chat_bp.route('/chat', methods=['POST'])
@cross_origin()
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        conversation_history = data.get('conversation_history', [])
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Generate response using trained knowledge
        response = get_ai_response(message, conversation_history)
        
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/chat/quick-action', methods=['POST'])
@cross_origin()
def quick_action():
    try:
        data = request.get_json()
        action = data.get('action', '')
        
        # Map quick actions to responses using AI response function
        if action == 'show_products':
            response = get_ai_response('show products')
        elif action == 'shipping_info':
            response = get_ai_response('shipping info')
        elif action == 'return_policy':
            response = get_ai_response('return policy')
        elif action == 'product_care':
            response = get_ai_response('product care')
        else:
            response = {
                "message": "I'm not sure about that action. How can I help you?",
                "type": "general"
            }
        
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/products', methods=['GET'])
@cross_origin()
def get_products():
    """Get all products from knowledge base"""
    try:
        knowledge_base = training_service.load_knowledge_base()
        if knowledge_base and 'product_catalog' in knowledge_base:
            products = []
            for product_id, product_info in knowledge_base['product_catalog'].items():
                products.append({
                    'id': product_id,
                    'title': product_info['title'],
                    'summary': product_info['summary'],
                    'price': product_info['price'],
                    'category': product_info['category'],
                    'features': product_info['features']
                })
            return jsonify({
                'success': True,
                'products': products
            })
        else:
            return jsonify({
                'success': True,
                'products': [],
                'message': 'No products found. Please train the model first.'
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/products/<product_id>', methods=['GET'])
@cross_origin()
def get_product(product_id):
    """Get specific product by ID from knowledge base"""
    try:
        knowledge_base = training_service.load_knowledge_base()
        if knowledge_base and 'product_catalog' in knowledge_base:
            product_info = knowledge_base['product_catalog'].get(str(product_id))
            if product_info:
                return jsonify({
                    'success': True,
                    'product': {
                        'id': product_id,
                        'title': product_info['title'],
                        'summary': product_info['summary'],
                        'price': product_info['price'],
                        'category': product_info['category'],
                        'features': product_info['features']
                    }
                })
        
        return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

