# Simplified training.py for debugging

from flask import Blueprint, jsonify
from flask_cors import cross_origin

training_bp = Blueprint('training', __name__)

@training_bp.route('/training/process-products', methods=['POST'])
@cross_origin()
def process_products_test():
    print("TEST: /api/training/process-products endpoint was successfully hit!")
    # Immediately return a success message without doing any real work
    return jsonify({
        'success': True,
        'message': 'TEST successful: Backend received the request.',
        'processed_count': 123, # Sending back dummy data
        'categories': ['Test Category']
    })