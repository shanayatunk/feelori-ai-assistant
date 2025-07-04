# src/routes/training.py - A complete test version

from flask import Blueprint, jsonify
from flask_cors import cross_origin
import time

training_bp = Blueprint('training', __name__)

@training_bp.route('/training/status', methods=['GET'])
@cross_origin()
def get_training_status_test():
    """A working test route for the initial status check."""
    print("TEST: /api/training/status endpoint was hit!")
    return jsonify({
        'success': True, 
        'training_status': {
            'is_trained': False,
            'files_status': {},
            'products_count': 0
        }
    })

@training_bp.route('/training/knowledge-base', methods=['GET'])
@cross_origin()
def get_knowledge_base_test():
    """A working test route for the initial knowledge base check."""
    print("TEST: /api/training/knowledge-base endpoint was hit!")
    return jsonify({
        'success': True, 
        'knowledge_base_summary': {
            'products_count': 0,
            'features_count': 0,
            'categories': [],
            'faq_topics': [],
            'created_at': time.time()
        }
    })

@training_bp.route('/training/process-products', methods=['POST'])
@cross_origin()
def process_products_test():
    """A working test route for the 'Process Products' button."""
    print("TEST: /api/training/process-products endpoint was successfully hit!")
    # Immediately return a success message
    return jsonify({
        'success': True,
        'message': 'TEST successful: Backend received the request.',
        'processed_count': 123, # Sending back dummy data
        'categories': ['Test Category']
    })

# Add placeholder routes for other functions your dashboard might call
@training_bp.route('/training/retrain', methods=['POST'])
@cross_origin()
def retrain_model_test():
    return jsonify({'success': True, 'message': 'Retrain test successful.'})

@training_bp.route('/training/search', methods=['POST'])
@cross_origin()
def search_products_test():
    return jsonify({'success': True, 'message': 'Search test successful.'})