# src/routes/shopify.py

from flask import Blueprint, jsonify
import requests
import os

shopify_bp = Blueprint('shopify', __name__)

# Load credentials from environment
SHOPIFY_STORE_NAME = os.getenv('SHOPIFY_STORE_NAME')
SHOPIFY_ADMIN_API_TOKEN = os.getenv('SHOPIFY_ADMIN_API_TOKEN')

def fetch_products_from_shopify():
    """This function fetches products and returns a Python dictionary, not a Flask response."""
    if not SHOPIFY_STORE_NAME or not SHOPIFY_ADMIN_API_TOKEN:
        return {"success": False, "error": "Missing Shopify credentials"}

    try:
        url = f"https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10/products.json"
        headers = {
            "X-Shopify-Access-Token": SHOPIFY_ADMIN_API_TOKEN,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raises an exception for bad status codes

        products = response.json().get("products", [])
        simplified_products = []
        for product in products:
            variant = product.get("variants", [])[0] if product.get("variants") else {}
            image = product.get("image") or {}
            simplified_products.append({
                "id": product.get("id"),
                "title": product.get("title"),
                "price": variant.get("price", "N/A"),
                "image": image.get("src", ""),
                "tags": product.get("tags", "")
            })
        
        return {"success": True, "products": simplified_products}

    except requests.RequestException as e:
        return {"success": False, "error": str(e)}

@shopify_bp.route('/shopify/products', methods=['GET'])
def get_shopify_products_route():
    """This is the API route that calls the function and returns a JSON response."""
    result = fetch_products_from_shopify()
    if not result.get('success'):
        return jsonify(result), 500
    return jsonify(result)
