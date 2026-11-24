# Stage 2: Formalisation, Implementation and Population

## Ontology Construction
The ontology (`stage-2/studentjobs.ttl`, prefix `sj:`) defines five core classes — `Job`, `Skill`, `Employer`, `WorkSchedule`, `Location` — with five `Job` subclasses: `Barista`, `RetailAssistant`, `KitchenAssistant`, `Waiter`, and `DeliveryDriver`. Object properties include `requiresSkill`, `offeredBy` (functional, inverse `offers`), `hasSchedule`, and `locatedIn`. Datatype properties capture `jobTitle`, `hourlyPay`, `hoursPerWeek`, and `requiresExperience`. Dublin Core terms and `owl:versionInfo` provide FAIR-compliant metadata.

## Axiomatisation and DL Reasoning
Three defined classes use necessary-and-sufficient conditions to trigger HermiT automated classification:

- **`StudentFriendlyJob`** – inferred for jobs where `requiresExperience = false` AND `hasSchedule` ∈ {Evening, Weekend, Flexible}.
- **`MultiSkillJob`** – inferred for jobs with ≥ 2 distinct `requiresSkill` values. Requires `owl:AllDifferent` on skill individuals to satisfy the Unique Name Assumption.
- **`WeekendJob`** – inferred for jobs with `hasSchedule sj:WeekendSchedule`.

Consistency verification: disjointness axiom (`owl:AllDisjointClasses`) on all top-level classes ensures an individual cannot be both a `Skill` and an `Employer`. HermiT confirms the ontology is satisfiable.

Evidence: screenshot at `stage-2/reasoner-classification.png`.

## External Alignment
- `sj:Job` → `rdfs:seeAlso schema:JobPosting`
- `sj:Skill` → `rdfs:seeAlso esco:Skill`
- `sj:Employer` → `rdfs:seeAlso schema:Organization`
- `sj:Location` → `rdfs:seeAlso schema:Place`

## Knowledge Graph Population
The ETL script `stage-2/populate.py` reads `stage-2/data/jobs.csv` and writes validated RDF triples (10 job individuals, 10 skill individuals, 3 employer individuals, 4 location individuals) to `stage-2/knowledge-graph.ttl`. It also asserts `owl:AllDifferent` axioms for each group of individuals.
