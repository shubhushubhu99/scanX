# app.py

from flask import Flask, render_template
from dotenv import load_dotenv

from api.analyze import analyze_api
from core.explain_dimension import dimension_api

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Register API blueprints
app.register_blueprint(analyze_api, url_prefix="/api")
app.register_blueprint(dimension_api, url_prefix="/api")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True, use_reloader=False)