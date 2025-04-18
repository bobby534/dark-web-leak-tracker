from flask import Blueprint, render_template, request
from app.utils import check_breaches

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None

    if request.method == "POST":
        query = request.form.get("email")
        if query:
            data = check_breaches(query)

            if data.get("success"):
                results = data
            else:
                error = data.get("error", "Something went wrong.")

    return render_template("index.html", results=results, error=error)
