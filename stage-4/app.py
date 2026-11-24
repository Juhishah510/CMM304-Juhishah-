"""Full-Featured Modern Flask Web Application for Exploring & Managing Scottish Student Jobs.
Interfaces with CSV and synchronizes the RDF Knowledge Graph automatically.
"""
from pathlib import Path
import csv
import sys
from flask import Flask, request, redirect, url_for, render_template, abort, Response

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "stage-2" / "data" / "jobs.csv"
TTL_PATH = ROOT / "stage-2" / "knowledge-graph.ttl"

# Import populate ETL script to synchronize knowledge graph on CRUD actions
sys.path.insert(0, str(ROOT / "stage-2"))
try:
    import populate
except ImportError:
    populate = None

app = Flask(__name__, template_folder="templates")
FIELDS = ["id", "title", "type", "employer", "schedule", "skills",
          "hourly_pay", "hours_per_week", "requires_experience", "location"]

JOB_TYPES = ["Barista", "RetailAssistant", "KitchenAssistant", "Waiter", "DeliveryDriver"]
SKILLS = ["Communication", "Teamwork", "TimeManagement", "CustomerService",
          "CashHandling", "FoodHygiene", "Multitasking", "ProblemSolving",
          "PhysicalStamina", "Numeracy"]
SCHEDULES = ["EveningSchedule", "WeekendSchedule", "FlexibleSchedule"]
EMPLOYERS = ["BrewHouseCafe", "NorthernThreads", "HarbourKitchen"]
LOCATIONS = ["Aberdeen", "Dundee", "Glasgow", "Edinburgh"]


def read_jobs():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_jobs(rows):
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    # Synchronize RDF knowledge graph automatically
    if populate and hasattr(populate, "main"):
        try:
            populate.main()
        except Exception as e:
            print(f"Warning: could not sync knowledge graph: {e}")


@app.get("/")
def index():
    all_rows = read_jobs()
    query = request.args.get("skill", "").strip().lower()
    location = request.args.get("location", "").strip()
    schedule = request.args.get("schedule", "").strip()
    student_friendly = request.args.get("student_friendly", "").strip().lower() == "true"

    rows = all_rows
    if query:
        query_words = [w for w in query.replace(";", " ").split() if len(w) > 1]
        def matches_job(j):
            searchable = f"{j.get('skills','')} {j.get('title','')} {j.get('type','')} {j.get('employer','')}".lower()
            if query in searchable:
                return True
            return any(w in searchable for w in query_words) if query_words else True
        rows = [j for j in rows if matches_job(j)]

    if location:
        rows = [j for j in rows if j.get("location") == location]
    if schedule:
        rows = [j for j in rows if j.get("schedule") == schedule]
    if student_friendly:
        rows = [
            j for j in rows
            if j.get("requires_experience", "").lower() == "false"
            and j.get("schedule") in ("WeekendSchedule", "EveningSchedule", "FlexibleSchedule")
        ]

    cities = sorted({j.get("location") for j in all_rows if j.get("location")})
    return render_template(
        "index.html",
        jobs=rows,
        cities=cities,
        skill=request.args.get("skill", ""),
        location=location,
        schedule=schedule,
        student_friendly=student_friendly,
    )


@app.get("/add")
def add_form():
    """Show the Add Vacancy form."""
    return render_template(
        "add.html",
        job_types=JOB_TYPES,
        skills=SKILLS,
        schedules=SCHEDULES,
        employers=EMPLOYERS,
        locations=LOCATIONS,
    )


@app.post("/add")
def add():
    """Handle the Add Vacancy form submission."""
    rows = read_jobs()
    data = {k: request.form.get(k, "").strip() for k in FIELDS if k != "id"}
    # Support multi-select skills (checkboxes) or single-value input
    skill_list = request.form.getlist("skills_multi")
    if skill_list:
        data["skills"] = ";".join(skill_list)
    ids = [int(j["id"][3:]) for j in rows if j.get("id", "").startswith("JOB") and j["id"][3:].isdigit()]
    next_num = max(ids + [0]) + 1
    data["id"] = f"JOB{next_num:02d}" if next_num < 100 else f"JOB{next_num}"
    rows.append(data)
    write_jobs(rows)
    return redirect(url_for("index"))


@app.route("/edit/<job_id>", methods=["GET", "POST"])
def edit(job_id):
    rows = read_jobs()
    job = next((j for j in rows if j["id"] == job_id), None)
    if job is None:
        abort(404)
    if request.method == "POST":
        for key in FIELDS:
            if key != "id":
                job[key] = request.form.get(key, "").strip()
        write_jobs(rows)
        return redirect(url_for("index"))
    return render_template(
        "edit.html",
        job=job,
        job_types=JOB_TYPES,
        skills=SKILLS,
        schedules=SCHEDULES,
        employers=EMPLOYERS,
        locations=LOCATIONS,
    )


@app.post("/delete/<job_id>")
def delete(job_id):
    write_jobs([j for j in read_jobs() if j["id"] != job_id])
    return redirect(url_for("index"))


@app.get("/graph")
def view_graph():
    """Serve the raw RDF Turtle knowledge graph."""
    if TTL_PATH.exists():
        return Response(TTL_PATH.read_text(encoding="utf-8"), mimetype="text/turtle")
    return "Knowledge graph has not been generated yet. Run populate.py first.", 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
