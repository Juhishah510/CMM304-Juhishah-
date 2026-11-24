"""Run every SPARQL query in stage-3/queries/ against the ontology and knowledge graph.

Requires rdflib (pip install -r requirements.txt). Run from the repository root:
    python stage-3/run_queries.py

CQ9 (student-friendly jobs) and CQ11 (federation) are not here: CQ9 needs the
reasoner's inferred types and CQ11 needs a SERVICE call to an external endpoint.
"""
import pathlib

from rdflib import Graph, URIRef

ROOT = pathlib.Path(__file__).resolve().parent.parent


def short(term):
    if isinstance(term, URIRef):
        return str(term).split("#")[-1]
    return str(term)


def main():
    graph = Graph()
    graph.parse(ROOT / "stage-2" / "studentjobs.ttl", format="turtle")
    graph.parse(ROOT / "stage-2" / "knowledge-graph.ttl", format="turtle")
    print(f"Loaded {len(graph)} triples\n")

    for path in sorted((ROOT / "stage-3" / "queries").glob("*.rq")):
        print("=" * 70)
        print(path.name)
        print("=" * 70)
        try:
            result = graph.query(path.read_text(encoding="utf-8"))
            headers = [str(v) for v in result.vars]
            rows = [[short(cell) for cell in row] for row in result]
            widths = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h)
                      for i, h in enumerate(headers)]
            print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
            for r in rows:
                print("  ".join(c.ljust(w) for c, w in zip(r, widths)))
            print(f"({len(rows)} rows)\n")
        except Exception as e:
            print(f"[Notice: Query could not be evaluated locally (e.g. requires live internet connection for SERVICE endpoint): {e}]\n")



if __name__ == "__main__":
    main()
