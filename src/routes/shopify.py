from flask import Blueprint, jsonify
import requests
import os

shopify_bp = Blueprint('shopify', __name__)

# Load credentials from environment variables set on Render
SHOPIFY_STORE_NAME = os.getenv('SHOPIFY_STORE_NAME')
SHOPIFY_ADMIN_API_TOKEN = os.getenv('SHOPIFY_ADMIN_API_TOKEN')

def fetch_products_from_shopify():
    """
    This internal function fetches all products from Shopify.
    It returns a Python dictionary, not a Flask response.
    """
    if not SHOPIFY_STORE_NAME or not SHOPIFY_ADMIN_API_TOKEN:
        print("Error: Missing Shopify credentials on the server.")
        return {"success": False, "error": "Missing Shopify credentials on server"}

    try:
        url = f"https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10/products.json"
        headers = {
            "X-Shopify-Access-Token": SHOPIFY_ADMIN_API_TOKEN,
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an exception for bad status codes

        products = response.json().get("products", [])
        return {"success": True, "products": products}

    except requests.RequestException as e:
        print(f"Error fetching from Shopify: {e}")
        return {"success": False, "error": f"Failed to fetch from Shopify: {str(e)}"}

@shopify_bp.route('/shopify/products', methods=['GET'])
def get_shopify_products_route():
    """
    This is the public API route that returns products as a JSON response.
    """
    result = fetch_products_from_shopify()
    if not result.get('success'):
        return jsonify(result), 500
    return jsonify(result)