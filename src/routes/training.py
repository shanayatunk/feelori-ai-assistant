from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from src.services.product_training import ProductTrainingService
import requests
import json

training_bp = Blueprint('training', __name__)

# Initialize training service
training_service = ProductTrainingService()

@training_bp.route('/training/process-products', methods=['POST'])
@cross_origin()
def process_products():
    """Process and train on product data"""
    try:
        # Get products from request or fetch from Shopify
        data = request.get_json()
        products = data.get('products', [])
        
        if not products:
            # Fetch products from Shopify endpoint
            try:
                response = requests.get('https://feelori-ai-assistant.onrender.com/api/shopify/products')
                shopify_data = response.json()
                if shopify_data.get('success'):
                    products = shopify_data.get('products', [])
            except Exception as e:
                return jsonify({'error': f'Failed to fetch products: {str(e)}'}), 500
        
        if not products:
            return jsonify({'error': 'No products provided for training'}), 400
        
        # Process the products
        processed_data = training_service.process_product_data(products)
        
        # Save processed data
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
        return jsonify({'error': str(e)}), 500

@training_bp.route('/training/knowledge-base', methods=['GET'])
@cross_origin()
def get_knowledge_base():
    """Get the current knowledge base"""
    try:
        knowledge_base = training_service.load_knowledge_base()
        
        if not knowledge_base:
            return jsonify({'error': 'No knowledge base found. Please process products first.'}), 404
        
        # Return summary information
        summary = {
            'products_count': len(knowledge_base.get('product_catalog', {})),
            'categories': knowledge_base.get('categories', []),
            'features_count': len(knowledge_base.get('common_features', [])),
            'price_ranges': knowledge_base.get('price_ranges', {}),
            'created_at': knowledge_base.get('created_at'),
            'faq_topics': list(knowledge_base.get('faq_responses', {}).keys())
        }
        
        return jsonify({
            'success': True,
            'knowledge_base_summary': summary
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/training/search', methods=['POST'])
@cross_origin()
def search_products():
    """Search products using the trained knowledge base"""
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

@training_bp.route('/training/recommendations', methods=['POST'])
@cross_origin()
def get_recommendations():
    """Get product recommendations by category"""
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

@training_bp.route('/training/status', methods=['GET'])
@cross_origin()
def get_training_status():
    """Get training status and statistics"""
    try:
        import os
        
        data_dir = training_service.data_dir
        files_status = {
            'products_file': os.path.exists(training_service.products_file),
            'knowledge_base_file': os.path.exists(training_service.knowledge_base_file),
            'training_data_file': os.path.exists(training_service.training_data_file)
        }
        
        knowledge_base = training_service.load_knowledge_base()
        
        status = {
            'is_trained': all(files_status.values()),
            'files_status': files_status,
            'data_directory': data_dir,
            'last_training': knowledge_base.get('created_at') if knowledge_base else None,
            'products_count': len(knowledge_base.get('product_catalog', {})) if knowledge_base else 0,
            'categories_count': len(knowledge_base.get('categories', [])) if knowledge_base else 0
        }
        
        return jsonify({
            'success': True,
            'training_status': status
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@training_bp.route('/training/retrain', methods=['POST'])
@cross_origin()
def retrain_model():
    """Retrain the model with latest product data"""
    try:
        # Fetch latest products from Shopify
        response = requests.get('https://feelori-ai-assistant.onrender.com/api/shopify/products')
        shopify_data = response.json()
        
        if not shopify_data.get('success'):
            return jsonify({'error': 'Failed to fetch products from Shopify'}), 500
        
        products = shopify_data.get('products', [])
        
        if not products:
            return jsonify({'error': 'No products found to train on'}), 400
        
        # Process and save
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

