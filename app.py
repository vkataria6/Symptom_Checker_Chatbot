from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from chat import get_response_info  

app = Flask(__name__)
CORS(app)


@app.route("/")
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
    return render_template("about_me.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    text = request.get_json().get("message")
    role, response, extra = get_response_info(text)

    # Return in the format expected by app.js
    return jsonify([role, [response], extra])


if __name__ == "__main__":
    app.run(debug=True)
