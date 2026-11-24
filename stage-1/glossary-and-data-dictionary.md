# Glossary and data dictionary

Namespace: `sj:` = `http://example.org/studentjobs#`

## Concepts

| Term | Kind | Definition |
|---|---|---|
| Job | Class | A paid part-time vacancy offered by an employer. |
| Barista | Subclass of Job | A job preparing and serving coffee and drinks. |
| RetailAssistant | Subclass of Job | A job serving customers and handling stock and tills in a shop. |
| KitchenAssistant | Subclass of Job | A job helping with food preparation and cleaning in a kitchen. |
| Waiter | Subclass of Job | A job taking orders and serving food and drink to customers. |
| DeliveryDriver | Subclass of Job | A job delivering goods or food to customers. |
| Skill | Class | A competence a person needs to do a job well. |
| Employer | Class | An organisation that offers jobs. |
| WorkSchedule | Class | A recurring pattern of working times. |
| MultiSkillJob | Defined class | A Job that requires at least two skills. |
| WeekendJob | Defined class | A Job whose schedule is the weekend schedule. |
| StudentFriendlyJob | Defined class | A Job with an evening, weekend or flexible schedule that needs no prior experience. |

## Relations and attributes

| Name | Kind | Domain | Range | Notes |
|---|---|---|---|---|
| requiresSkill | Object property | Job | Skill | A job may need several skills. |
| offeredBy | Object property | Job | Employer | Functional. Inverse: offers. |
| offers | Object property | Employer | Job | Inverse of offeredBy. |
| hasSchedule | Object property | Job | WorkSchedule | |
| jobTitle | Data property | Job | xsd:string | Advertised title. |
| hourlyPay | Data property | Job | xsd:decimal | Pounds per hour. Functional. |
| hoursPerWeek | Data property | Job | xsd:integer | Typical weekly hours. Functional. |
| requiresExperience | Data property | Job | xsd:boolean | True if prior experience is needed. Functional. |

## Individuals

| Group | Individuals |
|---|---|
| Skills (10) | Communication, Teamwork, TimeManagement, CustomerService, CashHandling, FoodHygiene, Multitasking, ProblemSolving, PhysicalStamina, Numeracy |
| Schedules (3) | EveningSchedule, WeekendSchedule, FlexibleSchedule |
| Employers (3) | BrewHouseCafe, NorthernThreads, HarbourKitchen (fictional) |
| Jobs (10) | BAR01, BAR02, RET01, RET02, KIT01, KIT02, WAI01, WAI02, DEL01, DEL02 (see `stage-2/data/jobs.csv`) |


## Location (added for Scotland-wide scope)

**Location**: a Scottish town or city where a specific vacancy is based. It is represented as an individual of the `Location` class and linked from a vacancy using `locatedIn`. Example individuals for testing are Aberdeen, Dundee, Glasgow and Edinburgh. These examples do not claim that the sample vacancies are real or currently available.

| Field / property | Type | Meaning | Example |
|---|---|---|---|
| `locatedIn` | Object property | Connects a job vacancy to its location | `BAR01 locatedIn Aberdeen` |
| `Location` | Class | Scottish town/city | `Dundee` |
| `cityName` | Optional data property | Display name of the city (can be supplied through `rdfs:label`) | `Glasgow` |
