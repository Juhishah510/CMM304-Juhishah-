# Technical Architecture & System Documentation: Scottish Student Jobs Knowledge Graph

**Author:** Juhi Shah (MSc Artificial Intelligence)  
**Institution:** School of Computing, Robert Gordon University (RGU), Aberdeen  
**Module:** CMM304 Knowledge Modelling and Reasoning  
**Target Repository:** `cmm304-student-jobs-kg-updated`  
**Licence:** Creative Commons Attribution 4.0 International ([CC BY 4.0](https://creativecommons.org/licenses/by/4.0/))

---

## 1. Executive Summary & System Purpose

This project implements an end-to-end, reasoning-capable **Symbolic Artificial Intelligence** system designed to model, infer, and query student part-time employment opportunities across four major Scottish cities: **Aberdeen, Dundee, Edinburgh, and Glasgow**.

Unlike conventional relational database management systems (RDBMS) or keyword-matching search engines, this system represents domain knowledge using the **Semantic Web standard technology stack** (RDF, RDFS, OWL 2 DL, and SPARQL). It combines mathematical formalisms from **Description Logic (DL)** with an automated DL tableau reasoner (**HermiT**) to perform deductive classification over vacancy individuals without manual labeling.

The system culminates in an interactive, consumer-facing **Flask web application** supporting multi-criteria search, Scottish location filtering, full **Create, Read, Update, Delete (CRUD)** operations, real-time automated knowledge graph synchronisation, and federated integration with **Wikidata**.

---

## 2. Ontology Engineering Methodology: The Middle-Out Approach

The conceptual model was developed following a **Middle-Out ontology engineering lifecycle**, addressing the dual challenges of excessive abstraction (top-down) and vocabulary fragmentation (bottom-up):

1. **Identification of Core Middle-Level Concepts:**  
   The primary entities governing student recruitment are tangible and concrete: `Job`, `Skill`, `Employer`, `WorkSchedule`, and `Location`. Establishing this stable middle layer provided immediate conceptual grounding.
2. **Upward Generalisation:**  
   The core entity `Job` was systematically aligned to standard global upper-level and domain vocabularies, notably `schema:JobPosting`, while `Employer` was linked to `schema:Organization`, and `Location` to `schema:Place`.
3. **Downward Decomposition:**  
   The abstract `Job` class was decomposed into five domain-specific subclasses representing common student roles: `Barista`, `RetailAssistant`, `KitchenAssistant`, `Waiter`, and `DeliveryDriver`. Vacancies were modeled as distinct named individuals (e.g., `BAR01`, `WAI01`).
4. **Vocabulary Normalisation:**  
   Unstructured terms gathered from Scottish job adverts were canonicalised to eliminate semantic drift. For example:
   * `"customer dialogue"`, `"interpersonal skills"` $\rightarrow$ `sj:Communication`
   * `"till operation"`, `"cash balancing"` $\rightarrow$ `sj:CashHandling`
   * `"handling lunch rush"` $\rightarrow$ `sj:Multitasking`
5. **CQ-Driven Validation:**  
   Every concept, relationship, and axiom was evaluated against a suite of 13 Competency Questions (CQs) to ensure ontological parsimony—unnecessary classes were pruned.

---

## 3. Knowledge Formalisation & Ontology Architecture

The ontology schema is authored in **OWL 2 Web Ontology Language (DL Profile)** and serialised in **Turtle (`.ttl`)** syntax under the base IRI `<http://example.org/studentjobs>` with prefix `sj:`.

### 3.1 Taxonomy and Class Hierarchy
* `owl:Thing`
  * `sj:Job`
    * `sj:Barista`
    * `sj:DeliveryDriver`
    * `sj:KitchenAssistant`
    * `sj:RetailAssistant`
    * `sj:Waiter`
    * `sj:StudentFriendlyJob` *(Defined Class / Inferred)*
    * `sj:MultiSkillJob` *(Defined Class / Inferred)*
    * `sj:WeekendJob` *(Defined Class / Inferred)*
  * `sj:Skill`
  * `sj:Employer`
  * `sj:WorkSchedule`
  * `sj:Location`

### 3.2 Property Specifications

| Property Identifier | OWL Type | Domain | Range | Characteristics | Semantics & Usage |
|:---|:---|:---|:---|:---|:---|
| `sj:requiresSkill` | ObjectProperty | `sj:Job` | `sj:Skill` | Non-functional | Connects a job vacancy to competencies it demands. |
| `sj:offeredBy` | ObjectProperty | `sj:Job` | `sj:Employer` | Functional | Inverse of `sj:offers`. A vacancy is offered by exactly one employer. |
| `sj:offers` | ObjectProperty | `sj:Employer` | `sj:Job` | Non-functional | Inverse of `sj:offeredBy`. |
| `sj:hasSchedule` | ObjectProperty | `sj:Job` | `sj:WorkSchedule` | Non-functional | Specifies recurring shift patterns (Evening, Weekend, Flexible). |
| `sj:locatedIn` | ObjectProperty | `sj:Job` | `sj:Location` | Functional | Connects a vacancy to its Scottish geographic host city. |
| `sj:jobTitle` | DatatypeProperty | `sj:Job` | `xsd:string` | Non-functional | Human-readable advertised job title. |
| `sj:hourlyPay` | DatatypeProperty | `sj:Job` | `xsd:decimal` | Functional | Rate of compensation in GBP (£/hr). |
| `sj:hoursPerWeek` | DatatypeProperty | `sj:Job` | `xsd:integer` | Functional | Expected contracted weekly commitment. |
| `sj:requiresExperience` | DatatypeProperty | `sj:Job` | `xsd:boolean` | Functional | Boolean flag (`true`/`false`) indicating if prior experience is required. |

### 3.3 FAIR Metadata Annotations
To conform to **FAIR (Findable, Accessible, Interoperable, Reusable)** principles, the ontology includes Dublin Core metadata:
* `dcterms:title`: "Student Part-Time Jobs Ontology"@en
* `dcterms:creator`: "Juhi Shah (2617188)"
* `dcterms:created`: "2026-10-21"^^xsd:date
* `dcterms:license`: `<https://creativecommons.org/licenses/by/4.0/>`
* `owl:versionInfo`: "0.1"

---

## 4. Description Logic (DL) Reasoning & Axiomatisation

The core strength of this ontology lies in its **Description Logic axiomatisation**, allowing automated reasoners (such as HermiT or Pellet) to deduce implicit truths.

### 4.1 Defined Classes (Equivalence Axioms)

1. **`StudentFriendlyJob` (Student Suitability Deduction):**  
   A job is defined as student-friendly if and only if it demands **no prior experience** and offers **evening, weekend, or flexible shift patterns**:
   $$\text{StudentFriendlyJob} \equiv \text{Job} \sqcap \exists \text{hasSchedule}.\{\text{EveningSchedule}, \text{WeekendSchedule}, \text{FlexibleSchedule}\} \sqcap \exists \text{requiresExperience}.\{\text{false}\}$$
   *Result:* Automatically infers 7 vacancies (`BAR01`, `BAR02`, `KIT01`, `KIT02`, `RET01`, `WAI02`, `DEL02`) without manual tagging.

2. **`MultiSkillJob` (Skill Complexity Deduction):**  
   A job demanding two or more distinct competencies:
   $$\text{MultiSkillJob} \equiv \text{Job} \sqcap (\ge 2\ \text{requiresSkill}.\text{Skill})$$

3. **`WeekendJob` (Shift Pattern Deduction):**  
   $$\text{WeekendJob} \equiv \text{Job} \sqcap \exists \text{hasSchedule}.\{\text{WeekendSchedule}\}$$

### 4.2 Disjointness & Consistency Constraints
To guarantee logical integrity and detect anomalies:
* `owl:AllDisjointClasses (sj:Employer sj:Job sj:Location sj:Skill sj:WorkSchedule)`  
  Ensures categorical purity: an individual instantiated as `Skill` can never simultaneously be an `Employer`.
* `owl:AllDisjointClasses (sj:Barista sj:DeliveryDriver sj:KitchenAssistant sj:RetailAssistant sj:Waiter)`  
  Enforces mutually exclusive job roles.

### 4.3 Open World Assumption (OWA) & `owl:AllDifferent`
In standard relational databases operating under the **Closed World Assumption (CWA)**, missing information is assumed false, and distinct strings are distinct entities.  
In contrast, OWL operates under the **Open World Assumption (OWA)** and lacks the **Unique Name Assumption (UNA)**: two distinct IRIs (`sj:Communication` and `sj:Teamwork`) could represent the same real-world entity unless explicitly declared distinct.  
*Architectural Solution:* The ETL script (`stage-2/populate.py`) dynamically injects `owl:AllDifferent` axioms over the sets of skills, schedules, employers, and locations. Without this, the cardinality constraint $\ge 2\ \text{requiresSkill}$ in `MultiSkillJob` would fail to trigger inferences in HermiT.

---

## 5. External Semantic Alignment & Interoperability

To prevent knowledge isolation, domain entities are formally aligned to recognised vocabularies:

* **Schema.org Alignment:**
  * `sj:Job` $\xrightarrow{\text{rdfs:seeAlso}}$ `schema:JobPosting`
  * `sj:Employer` $\xrightarrow{\text{rdfs:seeAlso}}$ `schema:Organization`
  * `sj:Location` $\xrightarrow{\text{rdfs:seeAlso}}$ `schema:Place`
  * `sj:hourlyPay` $\xrightarrow{\text{rdfs:seeAlso}}$ `schema:baseSalary`
  * `sj:jobTitle` $\xrightarrow{\text{rdfs:seeAlso}}$ `schema:title`
* **European ESCO Alignment:**
  * `sj:Skill` $\xrightarrow{\text{rdfs:seeAlso}}$ `http://data.europa.eu/esco/model#Skill` (European Skills, Competences, Qualifications and Occupations)
* *Design Justification:* Alignment is executed via `rdfs:seeAlso` rather than strict `owl:equivalentClass` to maintain autonomy and avoid importing external ontological commitments that could trigger unintended inconsistencies.

---

## 6. Automated ETL & Knowledge Graph Population Pipeline

The data ingestion workflow transforms raw tabular vacancy adverts into validated RDF triples:

```
[ stage-2/data/jobs.csv ]
           │
           ▼
[ stage-2/populate.py ] (Python 3 Standard Library)
           │
           ├─ Validates foreign keys against predefined SKILLS, SCHEDULES, EMPLOYERS, LOCATIONS
           ├─ Serialises typing triples (a sj:<JobType>)
           ├─ Serialises datatype literals (xsd:decimal, xsd:integer, xsd:boolean)
           └─ Injects owl:AllDifferent distinct member groupings
           │
           ▼
[ stage-2/knowledge-graph.ttl ] (Validated RDF Turtle Knowledge Graph)
```

---

## 7. Competency Question Verification via SPARQL

All requirements were verified through formal SPARQL queries executed via RDFlib against the integrated knowledge base (`studentjobs.ttl` + `knowledge-graph.ttl`):

| ID | Natural Language Competency Question | Formal Query Technique | Key SPARQL Construct | Validated Output |
|:---|:---|:---|:---|:---:|
| **CQ1** | Which jobs require communication skills? | Relational Pattern Matching | Triple pattern on `sj:Communication` | 6 vacancies |
| **CQ2** | Which jobs offer weekend schedules? | Temporal Pattern Matching | Triple pattern on `sj:WeekendSchedule` | 4 vacancies |
| **CQ3** | Which skills are required for a barista job? | Relational Projection | Class filter on `sj:Barista` + `DISTINCT` | 5 skills |
| **CQ4** | Which jobs require more than one skill? | Aggregation & Grouping | `COUNT(?skill)` + `HAVING(?count > 1)` | 9 vacancies |
| **CQ5** | Which jobs match a selected skill? | Parameterised Matching | Bound parameter on `sj:TimeManagement` | 4 vacancies |
| **CQ6** | Which jobs does each employer offer? | Multi-entity Join | Join across `sj:Employer` & `sj:Job` | 10 pairs |
| **CQ7** | Which jobs pay more than a given hourly rate? | Numeric Filtering | `FILTER(?pay > "11.40"^^xsd:decimal)` | 4 vacancies |
| **CQ8** | Which skills are shared across multiple job types? | Cross-Class Aggregation | `COUNT(DISTINCT ?jobType) > 1` | 5 shared skills |
| **CQ9** | Which jobs are student-friendly? (inferred) | DL Classification Retrieval | Query over defined class `sj:StudentFriendlyJob` | 7 vacancies (HermiT) |
| **CQ10**| Which jobs can someone with a given skill set do? | Set Containment / Negation | `FILTER NOT EXISTS` with negation | 4 vacancies |
| **CQ11**| What does Wikidata state about a job type? | SPARQL Federation | `SERVICE <https://query.wikidata.org/sparql>` | 3 descriptions |
| **CQ12**| Which jobs are located in a selected Scottish city? | Geographic Filtering | `FILTER CONTAINS(?city, "Aberdeen")` | 3 vacancies |
| **CQ13**| Which Scottish locations have vacancies requiring Communication? | Relational Cross-Filter | Multi-way join: `Skill` $\bowtie$ `Job` $\bowtie$ `Location` | 6 vacancies |

---

## 8. Federated Linked Data Integration (Wikidata)

Demonstrating Stage 4 advanced integration, **CQ11** (`stage-3/queries/cq11-federated-wikidata.rq`) bridges the local knowledge graph with the global Linked Open Data cloud via SPARQL 1.1 Federation:

```sparql
PREFIX sj:     <http://example.org/studentjobs#>
PREFIX wd:     <http://www.wikidata.org/entity/>
PREFIX schema: <http://schema.org/>

SELECT ?jobType ?wikidataItem ?externalDescription WHERE {
  VALUES (?jobType ?wikidataItem) {
    (sj:Barista        wd:Q108437)
    (sj:Waiter         wd:Q207471)
    (sj:DeliveryDriver wd:Q15978716)
  }
  SERVICE <https://query.wikidata.org/sparql> {
    ?wikidataItem schema:description ?externalDescription .
    FILTER (lang(?externalDescription) = "en")
  }
}
ORDER BY ?jobType
```
This dynamically enriches internal classifications with authoritative public semantic data without local data duplication.

---

## 9. Full-Stack Web Application Architecture

The consumer-facing portal is built with **Python Flask** and styled with **TailwindCSS**:

### 9.1 Application Architecture Flow
```
Browser Client (HTTP Request)
       │
       ▼
Flask Application Router (stage-4/app.py)
       ├── GET  /               ➔ Multi-faceted search & Scottish city filter
       ├── GET  /add            ➔ Render Add Vacancy Form
       ├── POST /add            ➔ Validate input, allocate ID, append to jobs.csv
       ├── GET  /edit/<job_id>  ➔ Render Edit Vacancy Form
       ├── POST /edit/<job_id>  ➔ Mutate vacancy attributes in jobs.csv
       ├── POST /delete/<job_id>➔ Remove vacancy row from jobs.csv
       └── GET  /graph          ➔ Stream raw RDF Turtle Knowledge Graph
       │
       ▼ (On Mutation: Add / Edit / Delete)
Automatic ETL Trigger (`write_jobs()` calls `populate.main()`)
       │
       ▼
Knowledge Graph Regeneration (`stage-2/knowledge-graph.ttl`)
```

### 9.2 Real-Time Semantic Synchronisation
Whenever an administrative or student user mutates vacancy data via the web interface:
1. The tabular datastore (`jobs.csv`) is atomically updated.
2. The `write_jobs()` handler triggers `populate.py`.
3. The RDF Knowledge Graph (`stage-2/knowledge-graph.ttl`) is regenerated and validated on-the-fly.
4. Subsequent SPARQL queries or triplestore consumers immediately reflect the updated state.

---

## 10. Multi-Dimensional Quality Evaluation

Following standard knowledge engineering quality metrics:

1. **Accuracy (100%):**  
   Every query result was programmatically cross-validated against ground-truth fixtures using `stage-3/expected_answers.py`. Zero false positives or false negatives were detected.
2. **Coverage:**  
   The ontology fully answers all 13 CQs covering geographical distribution, compensation, scheduling constraints, skill containment, and cross-domain federation.
3. **Coherency & Satisfiability:**  
   Verified via the HermiT reasoner in Protégé 5.5. No classes collapsed into `owl:Nothing` (unsatisfiable). Disjointness axioms prevent category confusion.
4. **Validity:**  
   Strict domain and range definitions on all object and datatype properties prevent ill-formed subject-predicate-object triples.
5. **Understandability:**  
   All entity labels use camelCase identifiers, annotated with explicit `rdfs:label` and `rdfs:comment` strings in English (`@en`).
6. **Pitfall Remediation (OOPS!):**  
   Evaluated against the OntOlogy Pitfall Scanner (OOPS!). Addressed common semantic pitfalls by declaring explicit inverse relationships (`sj:offeredBy` $\leftrightarrow$ `sj:offers`), typing all literals, and eliminating isolated concepts.

---

## 11. Complete File-by-File Repository Layout

```text
cmm304-student-jobs-kg-updated/
│
├── readme.md                           # Official RGU coursework document & setup instructions
├── reflective-statement.md             # 500-word critical reflection & GenAI transparent audit log
├── juhi.md                             # Comprehensive Hinglish viva preparation & concept walkthrough
├── PROJECT_GUIDE.md                    # This file — professional English technical architecture guide
├── requirements.txt                    # Python dependencies: rdflib, SPARQLWrapper, Flask
├── system-workflow-diagram.svg         # High-resolution vector diagram of the end-to-end architecture
├── reasoner-classification.png         # Machine-verified Protégé screenshot proving HermiT classification
├── view_ttl.py                         # Browser utility script for rendering RDF graphs
├── .gitignore                          # Standard git ignore file for Python/Protégé
│
├── stage-1-specification.md            # Stage 1 Report: Requirements, Middle-Out rationale, 13 CQs
├── stage-1/
│   ├── glossary-and-data-dictionary.md # Comprehensive dictionary of concepts, relations, and types
│   ├── knowledge-graph-diagram.mmd     # Mermaid source for conceptual model
│   └── knowledge-graph-diagram.svg     # Rendered vector diagram of conceptual model
│
├── stage-2-implementation.md           # Stage 2 Report: Formalisation, axioms, reasoning, metadata
├── stage-2/
│   ├── studentjobs.ttl                 # Core OWL 2 domain ontology schema (classes, axioms, annotations)
│   ├── knowledge-graph.ttl             # Populated RDF Turtle triples generated from jobs.csv
│   ├── studentjobs-merged.ttl          # Combined schema + data file for 1-click Protégé loading
│   ├── populate.py                     # Automated CSV-to-RDF ETL pipeline
│   ├── reasoner-classification.png     # Local copy of reasoner classification screenshot
│   ├── ontology-diagram.svg            # Visual class and property hierarchy diagram
│   └── data/
│       └── jobs.csv                    # Source student vacancy dataset across Scotland
│
├── stage-3-evaluation.md               # Stage 3 Report: All 13 SPARQL queries and execution tables
├── stage-3/
│   ├── run_queries.py                  # Automated test harness executing all 13 queries via RDFlib
│   ├── expected_answers.py             # Ground-truth verification script parsing jobs.csv
│   └── queries/                        # 13 formal SPARQL query files (.rq)
│       ├── cq01-communication.rq       # CQ1: Communication skills query
│       ├── cq02-weekend.rq             # CQ2: Weekend schedule query
│       ├── cq03-barista-skills.rq      # CQ3: Skills for Barista role
│       ├── cq04-multiple-skills.rq     # CQ4: Multi-skill vacancy aggregation
│       ├── cq05-selected-skill.rq      # CQ5: Parameterised skill matching
│       ├── cq06-employer-jobs.rq       # CQ6: Vacancies grouped by employer
│       ├── cq07-pay-above.rq           # CQ7: Hourly wage threshold filtering
│       ├── cq08-shared-skills.rq       # CQ8: Skills required across multiple job types
│       ├── cq09-student-friendly.rq    # CQ9: Inferred student-friendly job query
│       ├── cq10-skill-set.rq           # CQ10: Applicant skill set containment query
│       ├── cq11-federated-wikidata.rq  # CQ11: Federated SPARQL query to live Wikidata
│       ├── cq12-location.rq            # CQ12: Geographic Scottish city query
│       └── cq13-location-communication.rq # CQ13: City & skill cross-filter query
│
├── stage-4-webapp.md                   # Stage 4 Report: Flask service, CRUD mechanics, federation
└── stage-4/
    ├── app.py                          # Flask web service with search, filter, and CRUD API
    └── templates/                      # TailwindCSS responsive Jinja2 templates
        ├── index.html                  # Search, filter, and vacancy card dashboard
        ├── add.html                    # Add vacancy form with multi-skill checkboxes
        └── edit.html                   # Edit vacancy form for updating pay, hours, and attributes
```

---

## 12. Complete Execution & Reproduction Guide

### Step 1: Environment Activation
```powershell
# Navigate into the project repository
cd "cmm304-student-jobs-kg-updated"

# Activate the pre-configured virtual environment
.\.venv\Scripts\Activate.ps1

# (Optional: install dependencies if on a new machine)
pip install -r requirements.txt
```

### Step 2: Regenerate Knowledge Graph Triples (ETL)
```powershell
python stage-2\populate.py
```
*Expected Output:* `Wrote ...\stage-2\knowledge-graph.ttl`

### Step 3: Execute Automated SPARQL Test Suite
```powershell
python stage-3\run_queries.py
```
*Expected Output:* Executes all 13 queries sequentially and renders tabular results in the terminal.

### Step 4: Launch Web Application
```powershell
python stage-4\app.py
```
*Expected Output:* Server initializes on `http://127.0.0.1:5000`. Navigate to this URL in any web browser to interact with the full search, filter, add, edit, and delete functionality.

### Step 5: Verify HermiT Classification in Protégé
1. Launch **Protégé 5.5+**.
2. Go to **File $\rightarrow$ Open...** and select `stage-2/studentjobs-merged.ttl`.
3. Select **Reasoner $\rightarrow$ HermiT**.
4. Click **Reasoner $\rightarrow$ Start reasoner** (`Ctrl + R`).
5. Under **Entities $\rightarrow$ Classes**, observe automated classification of vacancies into `StudentFriendlyJob`, `MultiSkillJob`, and `WeekendJob`.
