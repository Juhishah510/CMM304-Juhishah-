# Reflective Statement & AI Audit Log

## GenAI Acknowledgement
I acknowledge the use of Anthropic Claude (https://claude.ai) and Google Antigravity to assist in this assessment. AI tools were used for brainstorming domain concepts, scaffolding ontology syntax, drafting Python scripts, and reviewing SPARQL queries. All design decisions, reasoner validations in Protégé, and final code reviews were conducted independently.

---

## AI Audit Log

| Date | Task | Key Prompt | AI Output | Error Found | My Fix | Decision |
|---|---|---|---|---|---|---|
| 2026-10-21 | Repository scaffold (Claude) | "Create starter layout for a student part-time jobs ontology with CSV, ETL and SPARQL." | Skeleton repo, draft ORSD, starter ontology, sample CSV. | Missing OWA handling; no Scottish location modelling. | Added `Location` class and 4 Scottish city individuals; inspected in Protégé. | Kept folder structure; expanded domain to Scotland-wide locations. |
| 2026-11-02 | Reasoning debugging (Claude) | "Why is HermiT not classifying vacancies into MultiSkillJob when skills are asserted?" | Suggested checking domain/range on `requiresSkill`. | AI missed that OWL's OWA means distinct IRIs are not automatically assumed distinct. | Diagnosed via Protégé reasoner explanation; added `owl:AllDifferent` axioms in `populate.py`. | Modified ETL to assert distinctness; MultiSkillJob now classifies correctly. |
| 2026-11-11 | SPARQL federation (Antigravity) | "Draft CQ9 (inferred) and CQ11 (Wikidata federation) SPARQL files." | Standard SPARQL files including a Wikidata `SERVICE` query. | RDFlib threw connection errors offline; CQ9 returned 0 rows without DL reasoner. | Diagnosed: RDFlib lacks DL tableau reasoning. Added error-tolerance in `run_queries.py`; cross-validated CQ9 with Protégé HermiT. | Kept federated query for live-triplestore use; documented HermiT-only nature of CQ9. |

---

## Critical Reflection

### 1. Tools and Experience
- **Protégé 5.x & HermiT:** Provided a visual environment for authoring OWL 2 constructs and witnessing automatic classification of `StudentFriendlyJob`, `MultiSkillJob`, and `WeekendJob`. Running the reasoner was essential for validating correctness — not just syntax validity.
- **RDFlib & SPARQL:** Enabled automated, reproducible query testing across all 13 competency questions, bridging the semantic graph with a programmatic test harness.
- **OOPS! Pitfall Scanner:** Detected missing inverse property declarations and untyped predicates in the initial ontology, prompting improvements to documentation quality.
- **Flask:** Provided a lightweight web layer demonstrating how end users interact with the underlying knowledge graph via full CRUD operations.

### 2. AI Errors and Fixes
The most critical AI failure occurred with Description Logic semantics: the AI generated a `MultiSkillJob` restriction but overlooked the OWL Open World Assumption. The ontology was syntactically valid, yet HermiT inferred zero members. Resolution required applying theoretical knowledge of the Unique Name Assumption and generating `owl:AllDifferent` axioms. A second issue arose when the AI assumed uniform network availability for SPARQL federation, omitting error handling for offline environments.

### 3. Human Design Decisions vs. AI Suggestions
Key architectural choices remained mine:
- Selecting **Middle-Out** over top-down abstractions to ground the model in real student needs.
- Keeping `Location` as a separate class from `Employer` to support multi-city employers.
- Rejecting n-ary skill reification in favour of direct `requiresSkill` relations to minimise query complexity.

### 4. Future Practice
I will integrate continuous semantic validation earlier — deploying automated reasoners during initial schema design rather than post-population. I will also design hybrid evaluation pipelines combining local triplestore endpoints with client-side applications from the outset.
