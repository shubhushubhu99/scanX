# app.py

from flask import Flask, render_template
from api.analyze import analyze_api

app = Flask(__name__)

app.register_blueprint(analyze_api, url_prefix="/api")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
