import os
from flask import Blueprint, flash, send_file, redirect, render_template, request
from app.utils import add_to_watchlist, check_breaches, generate_charts, clean_sources_light, save_search, save_query_log
import csv
import io
import json
from app.intelx_utils import search_intelx
from app.utils import merge_breach_sources


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
                # Clean LeakCheck results
                cleaned_sources = clean_sources_light(data["sources"])

                # Get IntelX results
                intelx_results = search_intelx(query)

                # Merge and sort
                merged_sources = merge_breach_sources(cleaned_sources, intelx_results)

                # Final output package
                data["sources"] = merged_sources  # Replaces with combined list
                results = data
                results["intelx"] = intelx_results
                results["query"] = query

                # Generate chart and save
                charts = generate_charts(data)
                save_search(query, data)
                save_query_log(query, data["found"])
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

from flask import redirect, flash

@main.route("/add_to_watchlist", methods=["POST"])
def add_to_watchlist_route():
    query = request.form.get("query")
    if not query:
        flash("Missing query", "danger")
        return redirect("/")

    success = add_to_watchlist(query)
    if success:
        flash(f"✅ Added '{query}' to watchlist", "success")
    else:
        flash(f"⚠️ '{query}' is already in watchlist", "info")

    return redirect("/")


@main.route("/remove_from_watchlist", methods=["POST"])
def remove_from_watchlist():
    item = request.form.get("item")
    file_path = "data/watchlist.json"

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            watchlist = json.load(f)

        if item in watchlist:
            watchlist.remove(item)
            with open(file_path, "w") as f:
                json.dump(watchlist, f, indent=4)
            flash(f"❌ Removed '{item}' from watchlist", "warning")

    return redirect("/")
