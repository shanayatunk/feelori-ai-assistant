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

    def load_knowledge_base(self):
        if os.path.exists(self.knowledge_base_file):
            with open(self.knowledge_base_file, 'r') as f:
                return json.load(f)
        return None

    def _clean_html(self, html_text: str) -> str:
        if not html_text:
            return ""
        clean_text = re.sub(r'<[^>]+>', '', html_text)
        return re.sub(r'\s+', ' ', clean_text).strip()

    def _parse_tags(self, tags_string: str) -> List[str]:
        if not tags_string:
            return []
        return [tag.strip() for tag in tags_string.split(',') if tag.strip()]

    def process_product_data(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        product_catalog = {}
        all_categories = set()

        for product in products:
            variant = product.get('variants', [{}])[0]
            product_id = str(product.get('id'))
            product_catalog[product_id] = {
                'id': product_id,
                'title': product.get('title', ''),
                'price': variant.get('price', 'N/A'),
                'tags': self._parse_tags(product.get('tags', '')),
                'product_type': product.get('product_type', ''),
                'summary': self._clean_html(product.get('body_html', ''))[:200] + '...'
            }
            if product.get('product_type'):
                all_categories.add(product.get('product_type'))
        
        knowledge_base = {
            'product_catalog': product_catalog,
            'categories': list(all_categories),
            'faq_responses': self._create_faq_responses(),
            'created_at': datetime.now().isoformat()
        }
        return knowledge_base

    def _create_faq_responses(self) -> Dict[str, str]:
        """Creates a dictionary of standard FAQ responses."""
        return {
            "shipping_info": "We offer standard shipping across India, which typically takes 3-5 business days. International shipping is planned for the future!",
            "return_policy": "We have a 30-day return policy. Items must be in their original condition with tags attached. Return shipping for defective items is covered by us.",
            "product_care": "For our jewelry, we recommend wiping it with a soft, dry cloth after use and storing it in the provided box. Avoid contact with water and perfume to ensure the 1-gram gold plating lasts for 1-2 years."
        }

    def save_processed_data(self, data: Dict[str, Any]) -> bool:
        """Saves the complete knowledge base to a file."""
        try:
            with open(self.knowledge_base_file, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Knowledge base saved successfully with {len(data.get('product_catalog', {}))} products.")
            return True
        except Exception as e:
            print(f"Error saving knowledge base: {e}")
            return False