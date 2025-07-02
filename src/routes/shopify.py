from flask import Blueprint, jsonify
import requests
import os

shopify_bp = Blueprint('shopify', __name__)

SHOPIFY_STORE_NAME = os.getenv('SHOPIFY_STORE_NAME')
SHOPIFY_ADMIN_API_TOKEN = os.getenv('SHOPIFY_ADMIN_API_TOKEN')

@shopify_bp.route('/shopify/products', methods=['GET'])
def get_shopify_products():
    if not SHOPIFY_STORE_NAME or not SHOPIFY_ADMIN_API_TOKEN:
        return jsonify({"error": "Missing Shopify credentials"}), 500

    try:
        url = f"https://{SHOPIFY_STORE_NAME}.myshopify.com/admin/api/2023-10/products.json"

        headers = {
            "X-Shopify-Access-Token": SHOPIFY_ADMIN_API_TOKEN,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        products = response.json().get("products", [])

        simplified_products = []
        for product in products:
            variant = product.get("variants", [])[0] if product.get("variants") else {}
            image = product.get("image", {})
            simplified_products.append({
                "id": product.get("id"),
                "title": product.get("title"),
                "price": variant.get("price", "N/A"),
                "image": image.get("src", ""),
                "tags": product.get("tags", "")
            })

        return jsonify(simplified_products)

    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500
