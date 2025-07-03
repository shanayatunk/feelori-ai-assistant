# src/routes/training.py

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.services.product_training import ProductTrainingService
import os

# Import the function directly instead of using requests
from src.routes.shopify import fetch_products_from_shopify

training_bp = Blueprint('training', __name__)
training_service = ProductTrainingService()

@training_bp.route('/process-products', methods=['POST'])
@cross_origin()
def process_products():
    try:
        data = request.get_json() or {}
        products = data.get('products', [])

        if not products:
            # Call the function directly
            shopify_data = fetch_products_from_shopify()
            if not shopify_data.get('success'):
                return jsonify({'error': shopify_data.get('error', 'Failed to fetch products')}), 500
            products = shopify_data.get('products', [])

        if not products:
            return jsonify({'error': 'No products found to train on'}), 400

        processed_data = training_service.process_product_data(products)
        success = training_service.save_processed_data(processed_data)

        if success:
            return jsonify({
                'success': True,
                'message': f'Successfully processed {len(products)} products',
                'processed_count': len(processed_data['products']),
                'categories': processed_data['categories'],
                'features_count': len(processed_data['features']),
                'tags_count': len(processed_data['tags'])
            })
        else:
            return jsonify({'error': 'Failed to save processed data'}), 500

    except Exception as e:
        # It's good practice to log the full error for debugging
        print(f"An error occurred in process_products: {e}")
        return jsonify({'error': 'An internal server error occurred.'}), 500

# (The rest of your training.py routes like /knowledge-base, /search, etc. remain the same)
# ... paste the rest of your original training.py file below this line ...

@training_bp.route('/knowledge-base', methods=['GET'])
@cross_origin()
def get_knowledge_base():
    try:
        knowledge_base = training_service.load_knowledge_base()
        if not knowledge_base:
            return jsonify({'error': 'No knowledge base found. Please process products first.'}), 404

        summary = {
            'products_count': len(knowledge_base.get('product_catalog', {})),
            'categories': knowledge_base.get('categories', []),
            'features_count': len(knowledge_base.get('common_features', [])),
            'price_ranges': knowledge_bease.get('price_ranges', {}),
            'created_at': knowledge_base.get('created_at'),
            'faq_topics': list(knowledge_base.get('faq_responses', {}).keys())
        }

        return jsonify({'success': True, 'knowledge_base_summary': summary})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/search', methods=['POST'])
@cross_origin()
def search_products():
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 5)

        if not query:
            return jsonify({'error': 'Query is required'}), 400

        results = training_service.search_products(query, limit)

        return jsonify({
            'success': True,
            'query': query,
            'results': results,
            'count': len(results)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/recommendations', methods=['POST'])
@cross_origin()
def get_recommendations():
    try:
        data = request.get_json()
        category = data.get('category', '')
        limit = data.get('limit', 3)

        if not category:
            return jsonify({'error': 'Category is required'}), 400

        recommendations = training_service.get_recommendations(category, limit)

        return jsonify({
            'success': True,
            'category': category,
            'recommendations': recommendations,
            'count': len(recommendations)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/status', methods=['GET'])
@cross_origin()
def get_training_status():
    try:
        files_status = {
            'products_file': os.path.exists(training_service.products_file),
            'knowledge_base_file': os.path.exists(training_service.knowledge_base_file),
            'training_data_file': os.path.exists(training_service.training_data_file)
        }

        knowledge_base = training_service.load_knowledge_base()
        status = {
            'is_trained': all(files_status.values()),
            'files_status': files_status,
            'data_directory': training_service.data_dir,
            'last_training': knowledge_base.get('created_at') if knowledge_base else None,
            'products_count': len(knowledge_base.get('product_catalog', {})) if knowledge_base else 0,
            'categories_count': len(knowledge_base.get('categories', [])) if knowledge_base else 0
        }

        return jsonify({'success': True, 'training_status': status})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/retrain', methods=['POST'])
@cross_origin()
def retrain_model():
    try:
        shopify_data = fetch_products_from_shopify()
        if not shopify_data.get('success'):
            return jsonify({'error': 'Invalid response from Shopify API'}), 500

        products = shopify_data.get('products', [])
        if not products:
            return jsonify({'error': 'No products found to train on'}), 400

        processed_data = training_service.process_product_data(products)
        success = training_service.save_processed_data(processed_data)

        if success:
            return jsonify({
                'success': True,
                'message': 'Model retrained successfully',
                'products_processed': len(products),
                'timestamp': processed_data['processed_at']
            })
        else:
            return jsonify({'error': 'Failed to save retrained data'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
