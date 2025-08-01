from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chat import get_response

app = Flask(__name__)
CORS(app)

@app.get("/")
def index_get():
    return render_template("base.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/about')
def about_us():
    return render_template("about_us.html")

@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    text_lower = text.lower().strip()

    # Load and process center data
    import json
    from difflib import get_close_matches
    with open("tri_state_medical_centers.json", "r") as f:
        centers = json.load(f)["intents"]
    city_to_centers = {}
    for center in centers:
        city = center["Address"].split(",")[-1].strip().lower()
        city_to_centers.setdefault(city, []).append((center["tag"], center["Address"]))

    matched_city = get_close_matches(text_lower, city_to_centers.keys(), n=1, cutoff=0.8)
    if matched_city:
        locations = city_to_centers[matched_city[0]][:3]
        return jsonify({"answer": ["center_results", locations, "", ""]})

    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)

if __name__ == "__main__":
    app.run(debug=True)