from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

items = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(items)

@app.route("/items", methods=["POST"])
def add_item():
    data = request.get_json()
    items.append(data)
    return jsonify(data), 201

@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    if 0 <= item_id < len(items):
        data = request.get_json()
        items[item_id]["price"] = data.get("price", items[item_id]["price"])
        return jsonify(items[item_id])
    return jsonify({"error": "Not found"}), 404

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    if 0 <= item_id < len(items):
        removed = items.pop(item_id)
        return jsonify(removed)
    return jsonify({"error": "Not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
