from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import requests
import json
import os

shopify_bp = Blueprint('shopify', __name__)

# Shopify configuration (these would be environment variables in production)
SHOPIFY_STORE_URL = os.getenv('SHOPIFY_STORE_URL', 'your-store.myshopify.com')
SHOPIFY_ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN', 'your-access-token')

# Mock Shopify data for demonstration
MOCK_SHOPIFY_PRODUCTS = [
    {
        "id": 1001,
        "title": "Feelori Comfort Pillow",
        "body_html": "<p>Ultra-soft memory foam pillow designed for optimal comfort and support. Perfect for side sleepers and back sleepers alike.</p>",
        "vendor": "Feelori",
        "product_type": "Bedding",
        "created_at": "2024-01-15T10:00:00-05:00",
        "handle": "feelori-comfort-pillow",
        "updated_at": "2024-01-15T10:00:00-05:00",
        "published_at": "2024-01-15T10:00:00-05:00",
        "template_suffix": None,
        "status": "active",
        "published_scope": "web",
        "tags": "comfort, memory foam, pillow, sleep, hypoallergenic",
        "admin_graphql_api_id": "gid://shopify/Product/1001",
        "variants": [
            {
                "id": 10001,
                "product_id": 1001,
                "title": "Default Title",
                "price": "49.99",
                "sku": "FCP-001",
                "position": 1,
                "inventory_policy": "deny",
                "compare_at_price": None,
                "fulfillment_service": "manual",
                "inventory_management": "shopify",
                "option1": "Default Title",
                "option2": None,
                "option3": None,
                "created_at": "2024-01-15T10:00:00-05:00",
                "updated_at": "2024-01-15T10:00:00-05:00",
                "taxable": True,
                "barcode": None,
                "grams": 1000,
                "image_id": None,
                "weight": 1.0,
                "weight_unit": "kg",
                "inventory_item_id": 20001,
                "inventory_quantity": 50,
                "old_inventory_quantity": 50,
                "requires_shipping": True,
                "admin_graphql_api_id": "gid://shopify/ProductVariant/10001"
            }
        ],
        "options": [
            {
                "id": 30001,
                "product_id": 1001,
                "name": "Title",
                "position": 1,
                "values": ["Default Title"]
            }
        ],
        "images": [
            {
                "id": 40001,
                "product_id": 1001,
                "position": 1,
                "created_at": "2024-01-15T10:00:00-05:00",
                "updated_at": "2024-01-15T10:00:00-05:00",
                "alt": "Feelori Comfort Pillow",
                "width": 800,
                "height": 600,
                "src": "https://cdn.shopify.com/s/files/1/0001/0001/products/feelori-comfort-pillow.jpg",
                "variant_ids": [],
                "admin_graphql_api_id": "gid://shopify/ProductImage/40001"
            }
        ],
        "image": {
            "id": 40001,
            "product_id": 1001,
            "position": 1,
            "created_at": "2024-01-15T10:00:00-05:00",
            "updated_at": "2024-01-15T10:00:00-05:00",
            "alt": "Feelori Comfort Pillow",
            "width": 800,
            "height": 600,
            "src": "https://cdn.shopify.com/s/files/1/0001/0001/products/feelori-comfort-pillow.jpg",
            "variant_ids": [],
            "admin_graphql_api_id": "gid://shopify/ProductImage/40001"
        }
    },
    {
        "id": 1002,
        "title": "Feelori Aromatherapy Diffuser",
        "body_html": "<p>Essential oil diffuser with LED lighting and timer settings. Create a relaxing atmosphere in any room.</p>",
        "vendor": "Feelori",
        "product_type": "Wellness",
        "created_at": "2024-01-16T10:00:00-05:00",
        "handle": "feelori-aromatherapy-diffuser",
        "updated_at": "2024-01-16T10:00:00-05:00",
        "published_at": "2024-01-16T10:00:00-05:00",
        "template_suffix": None,
        "status": "active",
        "published_scope": "web",
        "tags": "aromatherapy, diffuser, essential oils, wellness, LED",
        "admin_graphql_api_id": "gid://shopify/Product/1002",
        "variants": [
            {
                "id": 10002,
                "product_id": 1002,
                "title": "Default Title",
                "price": "79.99",
                "sku": "FAD-001",
                "position": 1,
                "inventory_policy": "deny",
                "compare_at_price": None,
                "fulfillment_service": "manual",
                "inventory_management": "shopify",
                "option1": "Default Title",
                "option2": None,
                "option3": None,
                "created_at": "2024-01-16T10:00:00-05:00",
                "updated_at": "2024-01-16T10:00:00-05:00",
                "taxable": True,
                "barcode": None,
                "grams": 500,
                "image_id": None,
                "weight": 0.5,
                "weight_unit": "kg",
                "inventory_item_id": 20002,
                "inventory_quantity": 30,
                "old_inventory_quantity": 30,
                "requires_shipping": True,
                "admin_graphql_api_id": "gid://shopify/ProductVariant/10002"
            }
        ],
        "options": [
            {
                "id": 30002,
                "product_id": 1002,
                "name": "Title",
                "position": 1,
                "values": ["Default Title"]
            }
        ],
        "images": [
            {
                "id": 40002,
                "product_id": 1002,
                "position": 1,
                "created_at": "2024-01-16T10:00:00-05:00",
                "updated_at": "2024-01-16T10:00:00-05:00",
                "alt": "Feelori Aromatherapy Diffuser",
                "width": 800,
                "height": 600,
                "src": "https://cdn.shopify.com/s/files/1/0001/0001/products/feelori-aromatherapy-diffuser.jpg",
                "variant_ids": [],
                "admin_graphql_api_id": "gid://shopify/ProductImage/40002"
            }
        ],
        "image": {
            "id": 40002,
            "product_id": 1002,
            "position": 1,
            "created_at": "2024-01-16T10:00:00-05:00",
            "updated_at": "2024-01-16T10:00:00-05:00",
            "alt": "Feelori Aromatherapy Diffuser",
            "width": 800,
            "height": 600,
            "src": "https://cdn.shopify.com/s/files/1/0001/0001/products/feelori-aromatherapy-diffuser.jpg",
            "variant_ids": [],
            "admin_graphql_api_id": "gid://shopify/ProductImage/40002"
        }
    }
]

def get_shopify_headers():
    """Get headers for Shopify API requests"""
    return {
        'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }

def make_shopify_request(endpoint, method='GET', data=None):
    """Make a request to Shopify API"""
    url = f"https://{SHOPIFY_STORE_URL}/admin/api/2023-10/{endpoint}"
    headers = get_shopify_headers()
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Shopify API request failed: {e}")
        return None

@shopify_bp.route('/shopify/products', methods=['GET'])
@cross_origin()
def get_shopify_products():
    """Get products from Shopify store"""
    try:
        # For demo purposes, return mock data
        # In production, this would make actual Shopify API calls
        if SHOPIFY_ACCESS_TOKEN == 'your-access-token':
            # Return mock data if no real credentials are configured
            return jsonify({
                'success': True,
                'products': MOCK_SHOPIFY_PRODUCTS,
                'source': 'mock'
            })
        
        # Make actual Shopify API call
        data = make_shopify_request('products.json')
        if data:
            return jsonify({
                'success': True,
                'products': data.get('products', []),
                'source': 'shopify'
            })
        else:
            return jsonify({'error': 'Failed to fetch products from Shopify'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@shopify_bp.route('/shopify/products/<int:product_id>', methods=['GET'])
@cross_origin()
def get_shopify_product(product_id):
    """Get specific product from Shopify store"""
    try:
        # For demo purposes, return mock data
        if SHOPIFY_ACCESS_TOKEN == 'your-access-token':
            product = next((p for p in MOCK_SHOPIFY_PRODUCTS if p['id'] == product_id), None)
            if not product:
                return jsonify({'error': 'Product not found'}), 404
            
            return jsonify({
                'success': True,
                'product': product,
                'source': 'mock'
            })
        
        # Make actual Shopify API call
        data = make_shopify_request(f'products/{product_id}.json')
        if data:
            return jsonify({
                'success': True,
                'product': data.get('product'),
                'source': 'shopify'
            })
        else:
            return jsonify({'error': 'Product not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@shopify_bp.route('/shopify/orders', methods=['GET'])
@cross_origin()
def get_shopify_orders():
    """Get orders from Shopify store"""
    try:
        # For demo purposes, return mock data
        mock_orders = [
            {
                "id": 5001,
                "email": "customer@example.com",
                "created_at": "2024-01-20T10:00:00-05:00",
                "updated_at": "2024-01-20T10:00:00-05:00",
                "number": 1001,
                "note": None,
                "token": "abc123",
                "gateway": "shopify_payments",
                "test": False,
                "total_price": "49.99",
                "subtotal_price": "49.99",
                "total_weight": 1000,
                "total_tax": "0.00",
                "taxes_included": False,
                "currency": "USD",
                "financial_status": "paid",
                "confirmed": True,
                "total_discounts": "0.00",
                "buyer_accepts_marketing": False,
                "name": "#1001",
                "referring_site": None,
                "landing_site": "/",
                "cancelled_at": None,
                "cancel_reason": None,
                "total_price_usd": "49.99",
                "checkout_token": "def456",
                "reference": None,
                "user_id": None,
                "location_id": None,
                "source_identifier": None,
                "source_url": None,
                "processed_at": "2024-01-20T10:00:00-05:00",
                "device_id": None,
                "phone": None,
                "customer_locale": "en",
                "app_id": 580111,
                "browser_ip": "192.168.1.1",
                "landing_site_ref": None,
                "order_number": 1001,
                "discount_applications": [],
                "discount_codes": [],
                "note_attributes": [],
                "payment_gateway_names": ["shopify_payments"],
                "processing_method": "direct",
                "checkout_id": 60001,
                "source_name": "web",
                "fulfillment_status": "fulfilled",
                "tax_lines": [],
                "tags": "",
                "contact_email": "customer@example.com",
                "order_status_url": "https://your-store.myshopify.com/orders/abc123",
                "presentment_currency": "USD",
                "total_line_items_price_set": {
                    "shop_money": {
                        "amount": "49.99",
                        "currency_code": "USD"
                    },
                    "presentment_money": {
                        "amount": "49.99",
                        "currency_code": "USD"
                    }
                },
                "total_discounts_set": {
                    "shop_money": {
                        "amount": "0.00",
                        "currency_code": "USD"
                    },
                    "presentment_money": {
                        "amount": "0.00",
                        "currency_code": "USD"
                    }
                },
                "total_shipping_price_set": {
                    "shop_money": {
                        "amount": "0.00",
                        "currency_code": "USD"
                    },
                    "presentment_money": {
                        "amount": "0.00",
                        "currency_code": "USD"
                    }
                },
                "subtotal_price_set": {
                    "shop_money": {
                        "amount": "49.99",
                        "currency_code": "USD"
                    },
                    "presentment_money": {
                        "amount": "49.99",
                        "currency_code": "USD"
                    }
                },
                "total_price_set": {
                    "shop_money": {
                        "amount": "49.99",
                        "currency_code": "USD"
                    },
                    "presentment_money": {
                        "amount": "49.99",
                        "currency_code": "USD"
                    }
                },
                "total_tax_set": {
                    "shop_money": {
                        "amount": "0.00",
                        "currency_code": "USD"
                    },
                    "presentment_money": {
                        "amount": "0.00",
                        "currency_code": "USD"
                    }
                },
                "line_items": [
                    {
                        "id": 70001,
                        "variant_id": 10001,
                        "title": "Feelori Comfort Pillow",
                        "quantity": 1,
                        "sku": "FCP-001",
                        "variant_title": None,
                        "vendor": "Feelori",
                        "fulfillment_service": "manual",
                        "product_id": 1001,
                        "requires_shipping": True,
                        "taxable": True,
                        "gift_card": False,
                        "name": "Feelori Comfort Pillow",
                        "variant_inventory_management": "shopify",
                        "properties": [],
                        "product_exists": True,
                        "fulfillable_quantity": 0,
                        "grams": 1000,
                        "price": "49.99",
                        "total_discount": "0.00",
                        "fulfillment_status": "fulfilled",
                        "price_set": {
                            "shop_money": {
                                "amount": "49.99",
                                "currency_code": "USD"
                            },
                            "presentment_money": {
                                "amount": "49.99",
                                "currency_code": "USD"
                            }
                        },
                        "total_discount_set": {
                            "shop_money": {
                                "amount": "0.00",
                                "currency_code": "USD"
                            },
                            "presentment_money": {
                                "amount": "0.00",
                                "currency_code": "USD"
                            }
                        },
                        "discount_allocations": [],
                        "duties": [],
                        "admin_graphql_api_id": "gid://shopify/LineItem/70001",
                        "tax_lines": []
                    }
                ]
            }
        ]
        
        if SHOPIFY_ACCESS_TOKEN == 'your-access-token':
            return jsonify({
                'success': True,
                'orders': mock_orders,
                'source': 'mock'
            })
        
        # Make actual Shopify API call
        data = make_shopify_request('orders.json')
        if data:
            return jsonify({
                'success': True,
                'orders': data.get('orders', []),
                'source': 'shopify'
            })
        else:
            return jsonify({'error': 'Failed to fetch orders from Shopify'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@shopify_bp.route('/shopify/orders/<int:order_id>', methods=['GET'])
@cross_origin()
def get_shopify_order(order_id):
    """Get specific order from Shopify store"""
    try:
        # For demo purposes, return mock data
        if SHOPIFY_ACCESS_TOKEN == 'your-access-token':
            # This would normally query the actual order
            return jsonify({
                'success': True,
                'order': {
                    'id': order_id,
                    'number': 1001,
                    'financial_status': 'paid',
                    'fulfillment_status': 'fulfilled',
                    'total_price': '49.99',
                    'created_at': '2024-01-20T10:00:00-05:00'
                },
                'source': 'mock'
            })
        
        # Make actual Shopify API call
        data = make_shopify_request(f'orders/{order_id}.json')
        if data:
            return jsonify({
                'success': True,
                'order': data.get('order'),
                'source': 'shopify'
            })
        else:
            return jsonify({'error': 'Order not found'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@shopify_bp.route('/shopify/sync', methods=['POST'])
@cross_origin()
def sync_shopify_data():
    """Sync product data from Shopify to local database"""
    try:
        # This would typically:
        # 1. Fetch all products from Shopify
        # 2. Update local database with product information
        # 3. Process product descriptions for AI training
        
        products_data = make_shopify_request('products.json')
        if not products_data and SHOPIFY_ACCESS_TOKEN == 'your-access-token':
            products_data = {'products': MOCK_SHOPIFY_PRODUCTS}
        
        if products_data:
            products = products_data.get('products', [])
            
            # Here you would typically save to database
            # For demo, we'll just return the count
            
            return jsonify({
                'success': True,
                'message': f'Successfully synced {len(products)} products',
                'products_count': len(products)
            })
        else:
            return jsonify({'error': 'Failed to sync products from Shopify'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@shopify_bp.route('/shopify/webhook', methods=['POST'])
@cross_origin()
def shopify_webhook():
    """Handle Shopify webhooks for real-time updates"""
    try:
        # Verify webhook authenticity (in production)
        # webhook_signature = request.headers.get('X-Shopify-Hmac-Sha256')
        # if not verify_webhook(request.data, webhook_signature):
        #     return jsonify({'error': 'Unauthorized'}), 401
        
        webhook_data = request.get_json()
        webhook_topic = request.headers.get('X-Shopify-Topic')
        
        # Handle different webhook topics
        if webhook_topic == 'products/create':
            # Handle new product creation
            product = webhook_data
            # Process and store product data
            pass
        elif webhook_topic == 'products/update':
            # Handle product updates
            product = webhook_data
            # Update stored product data
            pass
        elif webhook_topic == 'products/delete':
            # Handle product deletion
            product_id = webhook_data.get('id')
            # Remove product from local storage
            pass
        elif webhook_topic == 'orders/create':
            # Handle new order creation
            order = webhook_data
            # Process order data if needed
            pass
        
        return jsonify({'success': True, 'message': 'Webhook processed'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

