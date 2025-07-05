# src/services/product_training.py
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any

class ProductTrainingService:
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), '..', 'data')
        self.knowledge_base_file = os.path.join(self.data_dir, 'knowledge_base.json')
        os.makedirs(self.data_dir, exist_ok=True)
        self.knowledge_base = self._load_from_file()

    def _load_from_file(self):
        try:
            if os.path.exists(self.knowledge_base_file):
                with open(self.knowledge_base_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading knowledge base from file: {e}")
        return {}

    def get_knowledge_base(self):
        return self.knowledge_base

    def process_product_data(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        product_catalog = {}
        all_categories = set()
        for product in products:
            variant = product.get('variants', [{}])[0]
            product_id = str(product.get('id'))
            product_catalog[product_id] = {
                'id': product_id,
                'title': product.get('title', 'No Title'),
                'price': variant.get('price', '0.00'),
                'tags': self._parse_tags(product.get('tags', '')),
                'product_type': product.get('product_type', '')
            }
            if product.get('product_type'):
                all_categories.add(product.get('product_type'))

        return {
            'product_catalog': product_catalog,
            'categories': list(all_categories),
            'faq_responses': self._create_faq_responses(),
            'created_at': datetime.now().isoformat()
        }

    def _create_faq_responses(self) -> Dict[str, str]:
        return {
            "shipping_info": "We offer standard shipping across India (3-5 business days) and are planning to launch international shipping soon!",
            "return_policy": "Our policy allows for returns within 30 days of purchase, provided items are in original condition with tags. We cover return shipping for defective items.",
            "product_care": "To care for your jewelry, wipe it with a soft, dry cloth and store it in its box. Please avoid contact with water and perfume."
        }

    def save_processed_data(self, data: Dict[str, Any]) -> bool:
        try:
            with open(self.knowledge_base_file, 'w') as f:
                json.dump(data, f, indent=4)
            self.knowledge_base = data
            return True
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
            return False

    def _parse_tags(self, tags_string: str) -> List[str]:
        if not isinstance(tags_string, str): return []
        return [tag.strip() for tag in tags_string.split(',') if tag.strip()]