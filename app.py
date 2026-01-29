from flask import Flask, render_template, request
from api.analyze import analyze_target

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    target = request.form.get("target")

    if not target:
        return render_template(
            "error.html",
            error="No target provided"
        )

    result = analyze_target(target)

    if not result.get("success"):
        return render_template(
            "error.html",
            error=result.get("error", "Unknown error")
        )

    return render_template(
        "result.html",
        result=result
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        "error.html",
        error="Page not found"
    ), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template(
        "error.html",
        error="Internal server error"
    ), 500


if __name__ == "__main__":
    app.run(debug=True)
