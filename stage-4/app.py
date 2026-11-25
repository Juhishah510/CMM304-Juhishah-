"""Semantic Web Flask Application for Exploring & Managing Scottish Student Jobs.
Interfaces directly with the OWL 2 ontology (studentjobs.ttl) and RDF knowledge graph
(knowledge-graph.ttl) via RDFlib and SPARQL SELECT / INSERT DATA / DELETE WHERE queries.
"""
from pathlib import Path
from flask import Flask, request, redirect, url_for, render_template, abort, Response, jsonify
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

ROOT = Path(__file__).resolve().parent.parent
ONTOLOGY_PATH = ROOT / "stage-2" / "studentjobs.ttl"
KG_PATH = ROOT / "stage-2" / "knowledge-graph.ttl"

SJ = Namespace("http://example.org/studentjobs#")

app = Flask(__name__, template_folder="templates")


def load_graphs():
    """Load ontology schema + populated knowledge graph into an integrated RDFlib Graph."""
    schema = Graph()
    schema.parse(ONTOLOGY_PATH, format="turtle")

    data = Graph()
    if KG_PATH.exists():
        data.parse(KG_PATH, format="turtle")

    integrated = schema + data
    integrated.bind("sj", SJ)
    return schema, data, integrated


def save_data_graph(data_graph: Graph):
    """Persist the updated RDF knowledge graph back to stage-2/knowledge-graph.ttl."""
    data_graph.bind("sj", SJ)
    data_graph.serialize(destination=str(KG_PATH), format="turtle")


def local_name(uri_or_str) -> str:
    s = str(uri_or_str)
    return s.split("#")[-1] if "#" in s else s.rsplit("/", 1)[-1]


def get_ontology_metadata(integrated: Graph):
    """Query the ontology and KG via SPARQL to dynamically populate all UI options."""
    # Query asserted subclasses of sj:Job from the ontology
    q_types = """
    PREFIX sj:   <http://example.org/studentjobs#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?cls ?label WHERE {
      ?cls rdfs:subClassOf sj:Job ;
           rdfs:label ?label .
      FILTER (!isBlank(?cls))
    }
    ORDER BY ?label
    """
    job_types = [
        {"id": local_name(r.cls), "label": str(r.label)}
        for r in integrated.query(q_types)
    ]

    def query_individuals(class_name: str):
        q = f"""
        PREFIX sj:   <http://example.org/studentjobs#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT DISTINCT ?ind ?label WHERE {{
          ?ind a sj:{class_name} ;
               rdfs:label ?label .
        }}
        ORDER BY ?label
        """
        return [{"id": local_name(r.ind), "label": str(r.label)} for r in integrated.query(q)]

    return {
        "job_types": job_types,
        "skills": query_individuals("Skill"),
        "schedules": query_individuals("WorkSchedule"),
        "employers": query_individuals("Employer"),
        "locations": query_individuals("Location"),
    }


def query_jobs_from_kg(integrated: Graph):
    """Execute a SPARQL SELECT query against the integrated knowledge graph to retrieve all vacancies."""
    q_jobs = """
    PREFIX sj:   <http://example.org/studentjobs#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?job ?title ?jobType ?typeLabel ?employer ?employerLabel
           ?schedule ?scheduleLabel ?location ?locationLabel
           ?hourlyPay ?hoursPerWeek ?requiresExperience
    WHERE {
      ?job a ?jobType ;
           sj:jobTitle ?title ;
           sj:offeredBy ?employer ;
           sj:hasSchedule ?schedule ;
           sj:locatedIn ?location ;
           sj:hourlyPay ?hourlyPay ;
           sj:hoursPerWeek ?hoursPerWeek ;
           sj:requiresExperience ?requiresExperience .
      ?jobType rdfs:subClassOf sj:Job .
      OPTIONAL { ?jobType rdfs:label ?typeLabel . }
      OPTIONAL { ?employer rdfs:label ?employerLabel . }
      OPTIONAL { ?schedule rdfs:label ?scheduleLabel . }
      OPTIONAL { ?location rdfs:label ?locationLabel . }
      FILTER (!isBlank(?jobType))
    }
    ORDER BY ?job
    """
    q_skills = """
    PREFIX sj:   <http://example.org/studentjobs#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?job ?skill ?skillLabel WHERE {
      ?job sj:requiresSkill ?skill .
      OPTIONAL { ?skill rdfs:label ?skillLabel . }
    }
    ORDER BY ?skill
    """
    skills_by_job = {}
    for row in integrated.query(q_skills):
        jid = local_name(row.job)
        skills_by_job.setdefault(jid, []).append(local_name(row.skill))

    jobs = []
    for row in integrated.query(q_jobs):
        jid = local_name(row.job)
        sched_id = local_name(row.schedule)
        req_exp = str(row.requiresExperience).lower() == "true"
        skill_ids = skills_by_job.get(jid, [])
        # Mirror OWL StudentFriendlyJob & MultiSkillJob DL axioms
        is_student_friendly = (not req_exp) and (
            sched_id in ("EveningSchedule", "WeekendSchedule", "FlexibleSchedule")
        )
        jobs.append({
            "id": jid,
            "title": str(row.title),
            "type": local_name(row.jobType),
            "type_label": str(row.typeLabel or local_name(row.jobType)),
            "employer": local_name(row.employer),
            "employer_label": str(row.employerLabel or local_name(row.employer)),
            "schedule": sched_id,
            "schedule_label": str(row.scheduleLabel or sched_id),
            "location": local_name(row.location),
            "location_label": str(row.locationLabel or local_name(row.location)),
            "hourly_pay": str(row.hourlyPay),
            "hours_per_week": str(row.hoursPerWeek),
            "requires_experience": "true" if req_exp else "false",
            "skills": ";".join(skill_ids),
            "skill_list": skill_ids,
            "is_student_friendly": is_student_friendly,
            "is_multi_skill": len(set(skill_ids)) >= 2,
        })
    return jobs


@app.get("/")
def index():
    _, _, integrated = load_graphs()
    meta = get_ontology_metadata(integrated)
    all_jobs = query_jobs_from_kg(integrated)

    query_text = request.args.get("skill", "").strip().lower()
    location = request.args.get("location", "").strip()
    schedule = request.args.get("schedule", "").strip()
    student_friendly = request.args.get("student_friendly", "").strip().lower() == "true"

    rows = all_jobs
    if query_text:
        query_words = [w for w in query_text.replace(";", " ").split() if len(w) > 1]
        def matches_job(j):
            searchable = f"{j['skills']} {j['title']} {j['type']} {j['employer']} {j['employer_label']}".lower()
            if query_text in searchable:
                return True
            return any(w in searchable for w in query_words) if query_words else True
        rows = [j for j in rows if matches_job(j)]

    if location:
        rows = [j for j in rows if j["location"] == location]
    if schedule:
        rows = [j for j in rows if j["schedule"] == schedule]
    if student_friendly:
        rows = [j for j in rows if j["is_student_friendly"]]

    return render_template(
        "index.html",
        jobs=rows,
        cities=[loc["id"] for loc in meta["locations"]],
        meta=meta,
        triple_count=len(integrated),
        student_friendly_count=sum(1 for j in all_jobs if j["is_student_friendly"]),
        skill=request.args.get("skill", ""),
        location=location,
        schedule=schedule,
        student_friendly=student_friendly,
    )


def _sparql_insert_job(data_graph: Graph, job_id: str, form_data: dict, skill_list: list):
    """Execute a SPARQL INSERT DATA update to add a job individual to the RDF graph."""
    skill_triples = " ".join(f"sj:{job_id} sj:requiresSkill sj:{s} ." for s in skill_list if s)
    title_escaped = form_data["title"].replace("\\", "\\\\").replace('"', '\\"')
    exp_bool = "true" if form_data["requires_experience"].lower() == "true" else "false"

    update_query = f"""
    PREFIX sj:  <http://example.org/studentjobs#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    INSERT DATA {{
      sj:{job_id} a sj:{form_data['type']} ;
          sj:jobTitle "{title_escaped}" ;
          sj:offeredBy sj:{form_data['employer']} ;
          sj:hasSchedule sj:{form_data['schedule']} ;
          sj:locatedIn sj:{form_data['location']} ;
          sj:hourlyPay "{form_data['hourly_pay']}"^^xsd:decimal ;
          sj:hoursPerWeek "{form_data['hours_per_week']}"^^xsd:integer ;
          sj:requiresExperience "{exp_bool}"^^xsd:boolean .
      {skill_triples}
    }}
    """
    data_graph.update(update_query)


@app.get("/add")
def add_form():
    """Render the Add Vacancy form populated dynamically from the ontology."""
    _, _, integrated = load_graphs()
    meta = get_ontology_metadata(integrated)
    return render_template(
        "add.html",
        job_types=[t["id"] for t in meta["job_types"]],
        skills=[s["id"] for s in meta["skills"]],
        schedules=[s["id"] for s in meta["schedules"]],
        employers=[e["id"] for e in meta["employers"]],
        locations=[l["id"] for l in meta["locations"]],
        meta=meta,
    )


@app.post("/add")
def add():
    """Handle vacancy creation directly via SPARQL INSERT DATA on the RDF Knowledge Graph."""
    _, data_graph, integrated = load_graphs()
    existing_jobs = query_jobs_from_kg(integrated)
    ids = [int(j["id"][3:]) for j in existing_jobs if j["id"].startswith("JOB") and j["id"][3:].isdigit()]
    next_num = max(ids + [0]) + 1
    job_id = f"JOB{next_num:02d}" if next_num < 100 else f"JOB{next_num}"

    skill_list = request.form.getlist("skills_multi")
    if not skill_list:
        raw_skills = request.form.get("skills", "").strip()
        skill_list = [s.strip() for s in raw_skills.split(";") if s.strip()]

    form_data = {
        "title": request.form.get("title", "").strip(),
        "type": request.form.get("type", "").strip(),
        "employer": request.form.get("employer", "").strip(),
        "schedule": request.form.get("schedule", "").strip(),
        "location": request.form.get("location", "").strip(),
        "hourly_pay": request.form.get("hourly_pay", "11.50").strip(),
        "hours_per_week": request.form.get("hours_per_week", "12").strip(),
        "requires_experience": request.form.get("requires_experience", "false").strip(),
    }

    _sparql_insert_job(data_graph, job_id, form_data, skill_list)
    save_data_graph(data_graph)
    return redirect(url_for("index"))


@app.route("/edit/<job_id>", methods=["GET", "POST"])
def edit(job_id):
    """Read and update a vacancy directly in the RDF Knowledge Graph via SPARQL."""
    _, data_graph, integrated = load_graphs()
    meta = get_ontology_metadata(integrated)
    jobs = query_jobs_from_kg(integrated)
    job = next((j for j in jobs if j["id"] == job_id), None)
    if job is None:
        abort(404)

    if request.method == "POST":
        raw_skills = request.form.get("skills", "").strip()
        skill_list = [s.strip() for s in raw_skills.split(";") if s.strip()]
        form_data = {
            "title": request.form.get("title", "").strip(),
            "type": request.form.get("type", "").strip(),
            "employer": request.form.get("employer", "").strip(),
            "schedule": request.form.get("schedule", "").strip(),
            "location": request.form.get("location", "").strip(),
            "hourly_pay": request.form.get("hourly_pay", "11.50").strip(),
            "hours_per_week": request.form.get("hours_per_week", "12").strip(),
            "requires_experience": request.form.get("requires_experience", "false").strip(),
        }
        # Delete old triples for this job via SPARQL DELETE WHERE, then INSERT DATA
        data_graph.update(f"""
        PREFIX sj: <http://example.org/studentjobs#>
        DELETE WHERE {{ sj:{job_id} ?p ?o . }}
        """)
        _sparql_insert_job(data_graph, job_id, form_data, skill_list)
        save_data_graph(data_graph)
        return redirect(url_for("index"))

    return render_template("edit.html", job=job, meta=meta)


@app.post("/delete/<job_id>")
def delete(job_id):
    """Delete a vacancy individual from the RDF Knowledge Graph via SPARQL DELETE WHERE."""
    _, data_graph, _ = load_graphs()
    data_graph.update(f"""
    PREFIX sj: <http://example.org/studentjobs#>
    DELETE WHERE {{ sj:{job_id} ?p ?o . }}
    """)
    save_data_graph(data_graph)
    return redirect(url_for("index"))


@app.get("/api/federated/<job_type>")
def federated_wikidata(job_type):
    """Execute a live SPARQL SERVICE federated query against Wikidata for a job type."""
    _, _, integrated = load_graphs()
    q = f"""
    PREFIX sj:     <http://example.org/studentjobs#>
    PREFIX wd:     <http://www.wikidata.org/entity/>
    PREFIX schema: <http://schema.org/>
    SELECT ?externalDescription WHERE {{
      VALUES (?jt ?wikidataItem) {{
        (sj:Barista        wd:Q108437)
        (sj:Waiter         wd:Q207471)
        (sj:DeliveryDriver wd:Q15978716)
      }}
      FILTER (?jt = sj:{job_type})
      SERVICE <https://query.wikidata.org/sparql> {{
        ?wikidataItem schema:description ?externalDescription .
        FILTER (lang(?externalDescription) = "en")
      }}
    }}
    """
    try:
        results = [str(r.externalDescription) for r in integrated.query(q)]
        return jsonify({"job_type": job_type, "source": "Wikidata SPARQL Endpoint", "descriptions": results})
    except Exception as e:
        return jsonify({"job_type": job_type, "source": "Offline/Fallback", "error": str(e)}), 200


@app.get("/graph")
def view_graph():
    """Serve the live RDF Turtle knowledge graph."""
    if KG_PATH.exists():
        return Response(KG_PATH.read_text(encoding="utf-8"), mimetype="text/turtle")
    return "Knowledge graph not found.", 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
