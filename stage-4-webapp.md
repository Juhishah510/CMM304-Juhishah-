# Stage 4: Web Application, Data Management & Advanced Integration

## Application Aim and Functionality
The web application (`stage-4/app.py`) provides an interactive interface for students and career advisers to explore, filter, and manage part-time job vacancies across Scotland via a Python Flask service.

## Core Features and CRUD Capabilities
Complete **Create, Read, Update, and Delete (CRUD)** workflows:
- **Read:** Live search by skill keyword; filter by Scottish city and shift pattern.
- **Create:** Web form at `/add` adds new vacancies with full metadata validation.
- **Update:** Records are edited via `/edit/<job_id>`, modifying pay, hours, or skills.
- **Delete:** Positions are removed via POST `/delete/<job_id>`.
- **KG Sync:** Every write triggers `populate.py`, regenerating `stage-2/knowledge-graph.ttl` automatically.

## SPARQL Federation
Job types (Barista, Waiter, DeliveryDriver) are federated with **Wikidata** using the SPARQL `SERVICE` keyword (`stage-3/queries/cq11-federated-wikidata.rq`), enriching local data with authoritative external descriptions.

## How to Run
```bash
python -m pip install -r requirements.txt
python stage-4/app.py
```
Open a browser and navigate to: **`http://127.0.0.1:5000`**
