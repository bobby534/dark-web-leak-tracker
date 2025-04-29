from flask import Blueprint, render_template, request
from app.utils import check_breaches, generate_charts, clean_sources_light, save_search, save_query_log

main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None
    charts = {"timeline": None}

    if request.method == "POST":
        query = request.form.get("email")
        if query:
            data = check_breaches(query)

            if data.get("success"):
                cleaned_sources = clean_sources_light(data["sources"])
                data["sources"] = cleaned_sources  # Overwrite with cleaned sources
                results = data
                charts = generate_charts(data)
                save_search(query, data)  # Save search to history file
                save_query_log(query, data["found"]) # Queries only
            else:
                error = data.get("error", "Something went wrong.")

    return render_template("index.html", results=results, error=error, charts=charts)
