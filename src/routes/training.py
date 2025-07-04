from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.services.product_training import ProductTrainingService
import os
import time

# Import the internal function directly instead of using requests
from src.routes.shopify import fetch_products_from_shopify

training_bp = Blueprint('training', __name__)
training_service = ProductTrainingService()

@training_bp.route('/training/process-products', methods=['POST'])
@cross_origin()
def process_products():
    """Handles the 'Process Products' button click from the admin dashboard."""
    try:
        # Call the internal function directly to get products
        shopify_data = fetch_products_from_shopify()
        
        if not shopify_data.get('success'):
            return jsonify({'error': shopify_data.get('error', 'Failed to fetch products from Shopify')}), 500
        
        products = shopify_data.get('products', [])
        if not products:
            return jsonify({'error': 'No products were found in your Shopify store to train on.'}), 400

        # Process and save the data
        processed_data = training_service.process_product_data(products)
        training_service.save_processed_data(processed_data)

        return jsonify({
            'success': True,
            'message': f'Successfully processed {len(products)} products.',
            'processed_count': len(processed_data.get('products', [])),
            'categories': processed_data.get('categories', [])
        })

    except Exception as e:
        print(f"Error in /training/process-products: {str(e)}")
        return jsonify({'error': 'An unexpected internal error occurred during training.'}), 500

# --- Full working versions of the other dashboard routes ---

@training_bp.route('/training/status', methods=['GET'])
@cross_origin()
def get_training_status():
    """A working route for the initial status check."""
    files_status = {
        'products_file': os.path.exists(training_service.products_file),
        'knowledge_base_file': os.path.exists(training_service.knowledge_base_file),
    }
    knowledge_base = training_service.load_knowledge_base()
    status = {
        'is_trained': all(files_status.values()),
        'files_status': files_status,
        'products_count': len(knowledge_base.get('product_catalog', {})) if knowledge_base else 0,
    }
    return jsonify({'success': True, 'training_status': status})

@training_bp.route('/training/knowledge-base', methods=['GET'])
@cross_origin()
def get_knowledge_base():
    """A working route for the initial knowledge base check."""
    knowledge_base = training_service.load_knowledge_base()
    if not knowledge_base:
        return jsonify({'success': True, 'knowledge_base_summary': {
            'products_count': 0, 'features_count': 0, 'categories': [], 'faq_topics': [], 'created_at': None
        }})

    summary = {
        'products_count': len(knowledge_base.get('product_catalog', {})),
        'features_count': len(knowledge_base.get('common_features', [])),
        'categories': knowledge_base.get('categories', []),
        'faq_topics': list(knowledge_base.get('faq_responses', {}).keys()),
        'created_at': knowledge_base.get('created_at')
    }
    return jsonify({'success': True, 'knowledge_base_summary': summary})