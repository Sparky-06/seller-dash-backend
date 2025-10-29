from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
#from dotenv import load_dotenv

#load_dotenv()

app = Flask(__name__)
CORS(app)

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)


# ----------- ROUTES -----------

@app.route('/api/seller_dash', methods=['POST'])
def seller_dash():
    """Add a new product for a seller."""
    input_details = request.get_json()
    if not input_details:
        return jsonify({"error": "Invalid JSON body"}), 400

    # Trim strings
    input_details = {k: v.strip() if isinstance(v, str) else v for k, v in input_details.items()}

    # Validate required fields
    required_fields = ["username", "product_name", "price", "original_price", "brand", "category", "image"]
    missing = [f for f in required_fields if f not in input_details]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    # Validate prices
    if input_details["price"] < 0 or input_details["original_price"] < 0:
        return jsonify({"error": "Prices must be positive"}), 400

    # Check if username exists
    response = supabase.table("user_data").select("id").eq("username", input_details["username"]).execute()
    if not response.data:
        return jsonify({"error": "Username does not exist"}), 404

    # Insert product
    content = {
        "username": input_details["username"],
        "name": input_details["product_name"],
        "price": input_details["price"],
        "original_price": input_details["original_price"],
        "brand": input_details["brand"],
        "category": input_details["category"],
        "image": input_details["image"]
    }

    supabase.table("MarketPlace").insert(content).execute()
    return jsonify({"message": "Product successfully uploaded", "product": content}), 201


@app.route('/api/products/<username>', methods=['GET'])
def get_products(username):
    """Return all products for a seller (username)."""
    response = supabase.table("MarketPlace").select("*").eq("username", username).execute()
    return jsonify(response.data), 200


@app.route('/api/orders/<username>', methods=['GET'])
def get_orders(username):
    """Return all orders belonging to a seller (username)."""
    response = supabase.table("Orders").select("*").eq("seller_username", username).execute()
    return jsonify(response.data), 200


@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    supabase.table("MarketPlace").delete().eq("id", product_id).execute()
    return jsonify({"message": "Product deleted"}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

