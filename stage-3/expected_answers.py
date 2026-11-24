"""Work out the expected answers to the competency questions straight from the CSV.

This does NOT use SPARQL or RDF. It is an independent cross-check: the answers
printed by stage-3/run_queries.py should match these. Standard library only.
"""
import csv
import pathlib
from collections import defaultdict

CSV_PATH = pathlib.Path(__file__).resolve().parent.parent / "stage-2" / "data" / "jobs.csv"


def load():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        r["skills"] = [s for s in r["skills"].split(";") if s]
        r["pay"] = float(r["hourly_pay"])
    return rows


def show(title, items):
    print(f"{title}\n  " + (", ".join(items) if items else "(none)") + f"\n  [{len(items)}]\n")


def main():
    jobs = load()

    show("CQ1 jobs requiring Communication",
         [j["id"] for j in jobs if "Communication" in j["skills"]])
    show("CQ2 weekend jobs",
         [j["id"] for j in jobs if j["schedule"] == "WeekendSchedule"])
    show("CQ3 skills for Barista jobs",
         sorted({s for j in jobs if j["type"] == "Barista" for s in j["skills"]}))
    show("CQ4 jobs with more than one skill",
         [j["id"] for j in jobs if len(j["skills"]) > 1])
    show("CQ5 jobs requiring TimeManagement",
         [j["id"] for j in jobs if "TimeManagement" in j["skills"]])

    by_employer = defaultdict(list)
    for j in jobs:
        by_employer[j["employer"]].append(j["id"])
    show("CQ6 jobs per employer",
         [f"{e}: {' '.join(ids)}" for e, ids in sorted(by_employer.items())])

    show("CQ7 jobs paying more than 11.30",
         [j["id"] for j in jobs if j["pay"] > 11.30])

    types_per_skill = defaultdict(set)
    for j in jobs:
        for s in j["skills"]:
            types_per_skill[s].add(j["type"])
    show("CQ8 skills used by more than one job type",
         sorted(s for s, t in types_per_skill.items() if len(t) > 1))

    show("CQ9 student-friendly jobs (any of the three schedules, no experience needed)",
         [j["id"] for j in jobs
          if j["requires_experience"] == "false"
          and j["schedule"] in ("EveningSchedule", "WeekendSchedule", "FlexibleSchedule")])

    allowed = {"Communication", "Teamwork", "CustomerService", "TimeManagement", "Multitasking"}
    show("CQ10 jobs doable with " + ", ".join(sorted(allowed)),
         [j["id"] for j in jobs if set(j["skills"]) <= allowed])


if __name__ == "__main__":
    main()
