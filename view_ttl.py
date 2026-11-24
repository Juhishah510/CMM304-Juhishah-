#!/usr/bin/env python3
"""Simple viewer for Turtle (.ttl) files.

Run:
    python view_ttl.py path/to/file.ttl

It parses the Turtle file with rdflib, builds a tiny HTML page
showing all triples in a table, writes the page to the temporary
folder, and opens it in the default web browser.
"""
import sys
import pathlib
import tempfile
import webbrowser
from rdflib import Graph

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: view_ttl.py <file.ttl>")
        sys.exit(1)
    ttl_path = pathlib.Path(sys.argv[1])
    if not ttl_path.is_file():
        print(f"File not found: {ttl_path}")
        sys.exit(1)
    g = Graph()
    g.parse(str(ttl_path), format="turtle")
    # Build a simple HTML page
    html = ["<html><head><meta charset='utf-8'>",
            f"<title>{ttl_path.name}</title>",
            "<style>table{border-collapse:collapse;}th,td{border:1px solid #ccc;padding:4px;}</style>",
            "</head><body>",
            f"<h1>{ttl_path.name}</h1>",
            "<table><tr><th>Subject</th><th>Predicate</th><th>Object</th></tr>"]
    for s, p, o in g:
        html.append(f"<tr><td>{s.n3(g.namespace_manager)}</td><td>{p.n3(g.namespace_manager)}</td><td>{o.n3(g.namespace_manager)}</td></tr>")
    html.append("</table></body></html>")
    html_str = "\n".join(html)
    # Write to a temporary file
    tmp_path = pathlib.Path(tempfile.gettempdir()) / f"{ttl_path.stem}.html"
    tmp_path.write_text(html_str, encoding="utf-8")
    # Open in default browser
    webbrowser.open(f"file://{tmp_path}")

if __name__ == "__main__":
    main()

