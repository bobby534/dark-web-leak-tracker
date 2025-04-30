import os
from flask import Blueprint, send_file, redirect, render_template, request
from app.utils import add_to_watchlist, check_breaches, generate_charts, clean_sources_light, save_search, save_query_log
import csv
import io
import json
from app.intelx_utils import search_intelx


main = Blueprint("main", __name__)

@main.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None
    charts = {"timeline": None}
    watchlist = []
    watchlist_file = "data/watchlist.json"

    if request.method == "POST":
        query = request.form.get("email")
        if query:
            data = check_breaches(query)

            if data.get("success"):
                cleaned_sources = clean_sources_light(data["sources"])
                data["sources"] = cleaned_sources  # Overwrite with cleaned sources
                results = data
                results["query"] = query  # Add query to results for CSV export
                charts = generate_charts(data)
                save_search(query, data)  # Save search to history file
                save_query_log(query, data["found"]) # Queries only

                intelx_results = search_intelx(query)
                results["intelx"] = intelx_results
            else:
                error = data.get("error", "Something went wrong.")
    if os.path.exists(watchlist_file):
        with open(watchlist_file, "r") as f:
            try:
                watchlist = json.load(f)
            except json.JSONDecodeError:
                watchlist = []
                
    return render_template("index.html", results=results, error=error, charts=charts, watchlist=watchlist)


@main.route("/export_csv", methods=["POST"])
def export_csv():
    # Get data from form
    sources = request.form.get("sources_json")
    query = request.form.get("query")

    if not sources or not query:
        return "Missing data", 400

    # Convert JSON string to Python list
    import json
    try:
        source_list = json.loads(sources)
    except json.JSONDecodeError:
        return "Invalid JSON", 400

    # Create in-memory CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Breach Name", "Date"])

    for breach in source_list:
        writer.writerow([breach.get("name", "Unknown"), breach.get("date", "N/A")])

    output.seek(0)

    filename = f"breach_report_{query.replace('@', '_at_')}.csv"
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=filename
    )

@main.route("/add_to_watchlist", methods=["POST"])
def add_to_watchlist_route():
    query = request.form.get("query")
    if not query:
        return "Missing query", 400

    success = add_to_watchlist(query)
    message = "Added to watchlist" if success else "Already in watchlist"
    
    return redirect("/", code=302)  # Or flash message later
