from flask import Blueprint, render_template, request
from app.utils import check_breaches, generate_charts

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None
    charts = {"timeline": None}  # Only timeline now

    if request.method == "POST":
        query = request.form.get("email")
        if query:
            data = check_breaches(query)

            if data.get("success"):
                results = data
                charts = generate_charts(data)
            else:
                error = data.get("error", "Something went wrong.")

    return render_template("index.html", results=results, error=error, charts=charts)
