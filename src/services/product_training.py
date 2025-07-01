import json
import os
from typing import List, Dict, Any
from datetime import datetime
import re

class ProductTrainingService:
    """Service for training AI assistant on product data"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(os.path.dirname(__file__), '..', 'data')
        self.products_file = os.path.join(self.data_dir, 'products.json')
        self.knowledge_base_file = os.path.join(self.data_dir, 'knowledge_base.json')
        self.training_data_file = os.path.join(self.data_dir, 'training_data.json')
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
    
    def process_product_data(self, products: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process raw product data from Shopify into training format"""
        processed_data = {
            'products': [],
            'categories': set(),
            'tags': set(),
            'price_ranges': {},
            'features': set(),
            'processed_at': datetime.now().isoformat()
        }
        
        for product in products:
            processed_product = self._process_single_product(product)
            processed_data['products'].append(processed_product)
            
            # Collect categories and tags
            if processed_product.get('product_type'):
                processed_data['categories'].add(processed_product['product_type'])
            
            if processed_product.get('tags'):
                processed_data['tags'].update(processed_product['tags'])
            
            # Collect features from description
            if processed_product.get('features'):
                processed_data['features'].update(processed_product['features'])
        
        # Convert sets to lists for JSON serialization
        processed_data['categories'] = list(processed_data['categories'])
        processed_data['tags'] = list(processed_data['tags'])
        processed_data['features'] = list(processed_data['features'])
        
        return processed_data
    
    def _process_single_product(self, product: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single product into training format"""
        # Extract basic information
        processed = {
            'id': product.get('id'),
            'title': product.get('title', ''),
            'description': self._clean_html(product.get('body_html', '')),
            'product_type': product.get('product_type', ''),
            'vendor': product.get('vendor', ''),
            'tags': self._parse_tags(product.get('tags', '')),
            'handle': product.get('handle', ''),
            'status': product.get('status', 'active')
        }
        
        # Extract pricing information
        if product.get('variants') and len(product['variants']) > 0:
            variant = product['variants'][0]
            processed['price'] = float(variant.get('price', 0))
            processed['sku'] = variant.get('sku', '')
            processed['inventory_quantity'] = variant.get('inventory_quantity', 0)
            processed['weight'] = variant.get('weight', 0)
            processed['weight_unit'] = variant.get('weight_unit', 'kg')
        
        # Extract features from description
        processed['features'] = self._extract_features(processed['description'])
        
        # Create searchable text
        processed['searchable_text'] = self._create_searchable_text(processed)
        
        # Generate product summary for AI
        processed['ai_summary'] = self._generate_ai_summary(processed)
        
        return processed
    
    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags and clean text"""
        if not html_text:
            return ""
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', html_text)
        
        # Clean up whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        return clean_text
    
    def _parse_tags(self, tags_string: str) -> List[str]:
        """Parse comma-separated tags"""
        if not tags_string:
            return []
        
        return [tag.strip() for tag in tags_string.split(',') if tag.strip()]
    
    def _extract_features(self, description: str) -> List[str]:
        """Extract product features from description"""
        features = []
        
        # Common feature keywords
        feature_keywords = [
            'memory foam', 'hypoallergenic', 'machine washable', 'breathable',
            'ergonomic', 'adjustable', 'portable', 'wireless', 'rechargeable',
            'waterproof', 'durable', 'lightweight', 'compact', 'premium',
            'natural', 'organic', 'eco-friendly', 'sustainable', 'antibacterial',
            'temperature control', 'pressure relief', 'support', 'comfort',
            'soft', 'firm', 'medium', 'plush', 'cooling', 'warming'
        ]
        
        description_lower = description.lower()
        
        for keyword in feature_keywords:
            if keyword in description_lower:
                features.append(keyword)
        
        return features
    
    def _create_searchable_text(self, product: Dict[str, Any]) -> str:
        """Create searchable text combining all product information"""
        searchable_parts = [
            product.get('title', ''),
            product.get('description', ''),
            product.get('product_type', ''),
            product.get('vendor', ''),
            ' '.join(product.get('tags', [])),
            ' '.join(product.get('features', [])),
            product.get('sku', '')
        ]
        
        return ' '.join(filter(None, searchable_parts)).lower()
    
    def _generate_ai_summary(self, product: Dict[str, Any]) -> str:
        """Generate AI-friendly product summary"""
        title = product.get('title', 'Product')
        price = product.get('price', 0)
        description = product.get('description', '')
        features = product.get('features', [])
        product_type = product.get('product_type', '')
        
        summary_parts = [f"{title} is a {product_type.lower()} priced at ${price:.2f}."]
        
        if description:
            # Take first sentence or first 100 characters
            desc_summary = description.split('.')[0][:100]
            if len(desc_summary) < len(description):
                desc_summary += "..."
            summary_parts.append(desc_summary)
        
        if features:
            summary_parts.append(f"Key features include: {', '.join(features[:5])}.")
        
        return ' '.join(summary_parts)
    
    def save_processed_data(self, processed_data: Dict[str, Any]) -> bool:
        """Save processed data to files"""
        try:
            # Save products data
            with open(self.products_file, 'w') as f:
                json.dump(processed_data, f, indent=2)
            
            # Create knowledge base
            knowledge_base = self._create_knowledge_base(processed_data)
            with open(self.knowledge_base_file, 'w') as f:
                json.dump(knowledge_base, f, indent=2)
            
            # Create training data for AI responses
            training_data = self._create_training_data(processed_data)
            with open(self.training_data_file, 'w') as f:
                json.dump(training_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving processed data: {e}")
            return False
    
    def _create_knowledge_base(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create knowledge base for AI assistant"""
        knowledge_base = {
            'product_catalog': {},
            'categories': processed_data['categories'],
            'common_features': processed_data['features'],
            'price_ranges': self._calculate_price_ranges(processed_data['products']),
            'product_recommendations': self._create_recommendation_rules(processed_data['products']),
            'faq_responses': self._create_faq_responses(processed_data),
            'created_at': datetime.now().isoformat()
        }
        
        # Index products by various attributes
        for product in processed_data['products']:
            product_id = str(product['id'])
            knowledge_base['product_catalog'][product_id] = {
                'title': product['title'],
                'summary': product['ai_summary'],
                'price': product.get('price', 0),
                'category': product.get('product_type', ''),
                'features': product.get('features', []),
                'tags': product.get('tags', []),
                'searchable_text': product.get('searchable_text', '')
            }
        
        return knowledge_base
    
    def _calculate_price_ranges(self, products: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Calculate price ranges by category"""
        price_ranges = {}
        
        # Group products by category
        categories = {}
        for product in products:
            category = product.get('product_type', 'Other')
            price = product.get('price', 0)
            
            if category not in categories:
                categories[category] = []
            categories[category].append(price)
        
        # Calculate ranges for each category
        for category, prices in categories.items():
            if prices:
                price_ranges[category] = {
                    'min': min(prices),
                    'max': max(prices),
                    'avg': sum(prices) / len(prices)
                }
        
        return price_ranges
    
    def _create_recommendation_rules(self, products: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Create product recommendation rules"""
        recommendations = {
            'sleep_related': [],
            'wellness_related': [],
            'comfort_related': [],
            'budget_friendly': [],
            'premium': []
        }
        
        for product in products:
            product_id = str(product['id'])
            title = product.get('title', '').lower()
            features = [f.lower() for f in product.get('features', [])]
            price = product.get('price', 0)
            
            # Categorize products for recommendations
            if any(keyword in title for keyword in ['pillow', 'sleep', 'bed', 'blanket']):
                recommendations['sleep_related'].append(product_id)
            
            if any(keyword in title for keyword in ['wellness', 'therapy', 'diffuser', 'aromatherapy']):
                recommendations['wellness_related'].append(product_id)
            
            if any(feature in features for feature in ['comfort', 'soft', 'memory foam']):
                recommendations['comfort_related'].append(product_id)
            
            if price < 50:
                recommendations['budget_friendly'].append(product_id)
            elif price > 100:
                recommendations['premium'].append(product_id)
        
        return recommendations
    
    def _create_faq_responses(self, processed_data: Dict[str, Any]) -> Dict[str, str]:
        """Create FAQ responses based on product data"""
        categories = processed_data['categories']
        features = processed_data['features']
        
        faq_responses = {
            'shipping_info': "We offer free shipping on orders over $50. Standard shipping takes 3-5 business days, and express shipping takes 1-2 business days.",
            'return_policy': "We have a 30-day return policy. Items must be in original condition with tags attached. Return shipping is free for defective items.",
            'product_care': "Care instructions vary by product. Most fabric items are machine washable on gentle cycle. Check individual product pages for specific care instructions.",
            'warranty': "All products come with a 1-year manufacturer warranty covering defects in materials and workmanship."
        }
        
        # Add category-specific responses
        if 'Bedding' in categories:
            faq_responses['pillow_care'] = "Pillows should be fluffed daily and washed every 3-6 months. Use a gentle cycle with mild detergent."
        
        if 'Wellness' in categories:
            faq_responses['diffuser_usage'] = "Fill the diffuser with water up to the max line, add 3-5 drops of essential oil, and select your preferred timer setting."
        
        return faq_responses
    
    def _create_training_data(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create training data for AI responses"""
        training_data = {
            'product_queries': [],
            'recommendation_scenarios': [],
            'feature_explanations': {},
            'created_at': datetime.now().isoformat()
        }
        
        # Generate product query examples
        for product in processed_data['products']:
            training_data['product_queries'].extend([
                {
                    'query': f"Tell me about {product['title']}",
                    'response': product['ai_summary'],
                    'product_id': product['id']
                },
                {
                    'query': f"What are the features of {product['title']}?",
                    'response': f"The {product['title']} features: {', '.join(product.get('features', []))}",
                    'product_id': product['id']
                },
                {
                    'query': f"How much does {product['title']} cost?",
                    'response': f"The {product['title']} is priced at ${product.get('price', 0):.2f}",
                    'product_id': product['id']
                }
            ])
        
        # Generate recommendation scenarios
        training_data['recommendation_scenarios'] = [
            {
                'scenario': 'customer looking for better sleep',
                'keywords': ['sleep', 'pillow', 'comfort', 'rest'],
                'recommended_categories': ['Bedding'],
                'response_template': "For better sleep, I recommend our {product_name}. It's designed for {features} and costs ${price}."
            },
            {
                'scenario': 'customer wants relaxation products',
                'keywords': ['relax', 'stress', 'aromatherapy', 'wellness'],
                'recommended_categories': ['Wellness'],
                'response_template': "For relaxation, you might enjoy our {product_name}. It offers {features} and is priced at ${price}."
            }
        ]
        
        # Create feature explanations
        for feature in processed_data['features']:
            training_data['feature_explanations'][feature] = self._get_feature_explanation(feature)
        
        return training_data
    
    def _get_feature_explanation(self, feature: str) -> str:
        """Get explanation for a product feature"""
        explanations = {
            'memory foam': 'Memory foam contours to your body shape, providing personalized support and pressure relief.',
            'hypoallergenic': 'Hypoallergenic materials resist allergens like dust mites, mold, and bacteria.',
            'machine washable': 'Can be safely cleaned in a washing machine for easy maintenance.',
            'breathable': 'Allows air circulation to help regulate temperature and prevent overheating.',
            'ergonomic': 'Designed to support natural body posture and reduce strain.',
            'adjustable': 'Can be customized or modified to suit individual preferences.',
            'portable': 'Lightweight and easy to transport or move around.',
            'wireless': 'Operates without cables or cords for convenience and flexibility.',
            'rechargeable': 'Built-in battery that can be recharged for repeated use.',
            'waterproof': 'Protected against water damage and moisture.',
            'durable': 'Built to last with high-quality materials and construction.',
            'lightweight': 'Easy to handle and move due to reduced weight.',
            'compact': 'Space-saving design that fits in small areas.',
            'premium': 'High-end quality with superior materials and craftsmanship.',
            'natural': 'Made from naturally occurring materials without synthetic additives.',
            'organic': 'Produced without harmful chemicals or pesticides.',
            'eco-friendly': 'Environmentally responsible and sustainable.',
            'sustainable': 'Produced with minimal environmental impact.',
            'antibacterial': 'Treated to resist bacterial growth and maintain hygiene.',
            'temperature control': 'Helps regulate body temperature for optimal comfort.',
            'pressure relief': 'Reduces pressure points to prevent discomfort.',
            'support': 'Provides structural support for proper alignment.',
            'comfort': 'Designed for maximum comfort and user satisfaction.',
            'soft': 'Gentle and plush texture for comfort.',
            'firm': 'Provides solid support with minimal give.',
            'medium': 'Balanced feel between soft and firm.',
            'plush': 'Extra soft and luxurious feel.',
            'cooling': 'Helps dissipate heat to keep you cool.',
            'warming': 'Provides gentle warmth for comfort.'
        }
        
        return explanations.get(feature.lower(), f'{feature.title()} is a beneficial product feature.')
    
    def load_knowledge_base(self) -> Dict[str, Any]:
        """Load the knowledge base from file"""
        try:
            if os.path.exists(self.knowledge_base_file):
                with open(self.knowledge_base_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return {}
    
    def search_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search products based on query"""
        knowledge_base = self.load_knowledge_base()
        products = knowledge_base.get('product_catalog', {})
        
        query_lower = query.lower()
        matches = []
        
        for product_id, product_info in products.items():
            searchable_text = product_info.get('searchable_text', '')
            
            # Simple keyword matching
            if any(word in searchable_text for word in query_lower.split()):
                matches.append({
                    'id': product_id,
                    'title': product_info['title'],
                    'summary': product_info['summary'],
                    'price': product_info['price'],
                    'category': product_info['category'],
                    'features': product_info['features']
                })
        
        # Sort by relevance (simple implementation)
        matches.sort(key=lambda x: sum(1 for word in query_lower.split() if word in x['title'].lower()), reverse=True)
        
        return matches[:limit]
    
    def get_recommendations(self, category: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get product recommendations by category"""
        knowledge_base = self.load_knowledge_base()
        recommendations = knowledge_base.get('product_recommendations', {})
        products = knowledge_base.get('product_catalog', {})
        
        category_map = {
            'sleep': 'sleep_related',
            'wellness': 'wellness_related',
            'comfort': 'comfort_related',
            'budget': 'budget_friendly',
            'premium': 'premium'
        }
        
        rec_category = category_map.get(category.lower(), category.lower())
        product_ids = recommendations.get(rec_category, [])
        
        recommended_products = []
        for product_id in product_ids[:limit]:
            if product_id in products:
                product_info = products[product_id]
                recommended_products.append({
                    'id': product_id,
                    'title': product_info['title'],
                    'summary': product_info['summary'],
                    'price': product_info['price'],
                    'category': product_info['category']
                })
        
        return recommended_products

