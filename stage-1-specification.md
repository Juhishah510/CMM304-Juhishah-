# Stage 1: Specification

## 1. Modelling and Knowledge Acquisition Strategy

I adopted a **Middle-Out** ontology engineering approach for this domain. The core concepts — Job, Skill, Employer, WorkSchedule, and Location — are concrete and familiar from real student job adverts, making them a stable middle layer. Starting purely top-down would have introduced abstract upper classes that no competency question requires, adding unnecessary complexity. Starting purely bottom-up would have risked inconsistency across advert wording, requiring extensive normalisation without a guiding schema.

**How I applied it:**

1. **Acquire.** I collected 10 student job adverts from Scottish employers' careers pages, recording URLs and access dates. The CSV (`stage-2/data/jobs.csv`) contains these records.
2. **Extract and normalise.** Raw terms were merged: "good interpersonal skills" and "customer communication" → `Communication`; "till operations" → `CashHandling`; "thriving in peak lunch rushes" → `Multitasking`.
3. **Generalise upward.** Titles were grouped into types (Barista, RetailAssistant, KitchenAssistant, Waiter, DeliveryDriver) under `Job`, aligned to `schema:JobPosting`.
4. **Decompose downward.** Vacancies (individuals) were separated from job types (classes); skill levels (Essential/Desirable) were simplified to direct `requiresSkill` after reviewing CQs.
5. **Validate.** Each concept was tested against all 13 competency questions; unused concepts were removed.

---

## 2. Ontology Requirements Specification Document (ORSD)

**Purpose.** Represent part-time job vacancies open to students across Scotland, together with required skills, employers, shift schedules, and locations, so that students and software agents can query and reason over employment opportunities.

**Scope.** Approximately 5 job types, 10 skills, 3 employers, 3 schedule patterns, and vacancy details (hourly pay, weekly hours, prior experience requirement). Four Scottish cities: Aberdeen, Dundee, Edinburgh, Glasgow.

**Intentionally excluded.** Full-time and graduate careers, application tracking, educational qualifications, employment law, live vacancy feeds, personal CVs.

**Target users.** Students seeking part-time work; university careers advisers; and the Flask web application as a software consumer.

---

## 3. Competency Questions (CQs)

A minimum of 10 CQs is required; this ontology supports 13.

| ID | Question | Type | Priority |
|---|---|---|---|
| CQ1 | Which jobs require communication skills? | Lookup | High |
| CQ2 | Which jobs offer weekend schedules? | Lookup | High |
| CQ3 | Which skills are required for a barista job? | Relationship | High |
| CQ4 | Which jobs require more than one skill? | Aggregation | Medium |
| CQ5 | Which jobs match a selected skill? | Parameterised | High |
| CQ6 | Which jobs does each employer offer? | Relationship | Medium |
| CQ7 | Which jobs pay more than a given hourly rate? | Numerical filter | Medium |
| CQ8 | Which skills are required by more than one job type? | Aggregation | Medium |
| CQ9 | Which jobs are student-friendly? (inferred) | DL Inference | High |
| CQ10 | Which jobs can someone with a given skill set do? | Set containment | Medium |
| CQ11 | What does an external knowledge graph state about a job type? | Federation | Low |
| CQ12 | Which jobs are located in a selected Scottish city? | Parameterised lookup | High |
| CQ13 | Which Scottish locations have vacancies requiring Communication? | Relational filter | Medium |

---

## 4. Conceptual Model & Knowledge Acquisition

The full glossary and data dictionary are in [stage-1/glossary-and-data-dictionary.md](stage-1/glossary-and-data-dictionary.md).

**Key modelling decisions:**
- Job types are **classes** (Barista, Waiter, etc.) and individual vacancies are **individuals** (BAR01, WAI01, etc.) — this supports both class-level reasoning (CQ3: skills for all Barista jobs) and individual queries (CQ7: pay for a specific vacancy).
- Skills, schedules, and employers are **individuals** so SPARQL can join across them.
- `Location` is a **separate class** (not merged with Employer) because one employer may advertise vacancies in multiple Scottish cities.
- `StudentFriendlyJob`, `MultiSkillJob`, and `WeekendJob` are **defined classes** (necessary and sufficient conditions) so the HermiT reasoner can automatically classify vacancies into them.

**Taxonomy and relations diagram:**

```mermaid
classDiagram
  Job <|-- Barista
  Job <|-- RetailAssistant
  Job <|-- KitchenAssistant
  Job <|-- Waiter
  Job <|-- DeliveryDriver
  Job --> Skill : requiresSkill
  Job --> Employer : offeredBy
  Job --> WorkSchedule : hasSchedule
  Job --> Location : locatedIn
  class Job {
    jobTitle : string
    hourlyPay : decimal
    hoursPerWeek : integer
    requiresExperience : boolean
  }
  class Location {
    cityName : string
  }
```

---

## 5. Design Patterns & Reuse

- **N-ary relation pattern** (optional) for recording whether a skill is essential or desirable — omitted as only 2 of 10 adverts distinguished skill levels explicitly.
- **schema.org** (`schema:JobPosting`, `schema:Organization`, `schema:Place`) — web interoperability.
- **ESCO** (`esco:Skill`) — European labour-market skill taxonomy. Alignment via `rdfs:seeAlso` rather than strict `owl:equivalentClass`.
