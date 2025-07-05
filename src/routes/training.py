# src/routes/training.py
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.services import training_service
from src.routes.shopify import fetch_products_from_shopify

training_bp = Blueprint('training', __name__)

@training_bp.route('/training/process-products', methods=['POST'])
@cross_origin()
def process_products():
    try:
        shopify_data = fetch_products_from_shopify()
        if not shopify_data.get('success'):
            return jsonify({'error': shopify_data.get('error', 'Failed to fetch products')}), 500
        
        products = shopify_data.get('products', [])
        if not products:
            return jsonify({'error': 'No products found to train on.'}), 400

        processed_data = training_service.process_product_data(products)
        training_service.save_processed_data(processed_data)

        return jsonify({
            'success': True,
            'message': f'Successfully processed {len(products)} products.',
            'data': processed_data
        })
    except Exception as e:
        print(f"Error in /process-products: {str(e)}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

@training_bp.route('/training/status', methods=['GET'])
@cross_origin()
def get_training_status():
    knowledge_base = training_service.get_knowledge_base()
    status = {'is_trained': bool(knowledge_base), 'products_count': len(knowledge_base.get('product_catalog', {}))}
    return jsonify({'success': True, 'training_status': status})

@training_bp.route('/training/knowledge-base', methods=['GET'])
@cross_origin()
def get_knowledge_base():
    knowledge_base = training_service.get_knowledge_base()
    if not knowledge_base:
        return jsonify({'success': True, 'knowledge_base_summary': {}})
    summary = {
        'products_count': len(knowledge_base.get('product_catalog', {})),
        'categories': knowledge_base.get('categories', []),
        'faq_topics': list(knowledge_base.get('faq_responses', {}).keys()),
        'created_at': knowledge_base.get('created_at')
    }
    return jsonify({'success': True, 'knowledge_base_summary': summary})