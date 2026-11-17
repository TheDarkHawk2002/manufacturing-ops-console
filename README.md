# Manufacturing Operations Console

A small, fictional command-line workbench for reviewing manufacturing-application incidents and preparing a consistent handoff. It demonstrates structured triage, service-oriented communication, and operational documentation using synthetic data only.

## Scope

The sample models an application support workflow without connecting to real systems. It does not implement MES, SAP, monitoring integrations, authentication, or production support. Incident priorities are derived from transparent rules; users remain responsible for validating the impact and next action.

## Requirements

- Python 3.11 or newer
- Standard library only

## Run

```powershell
python src/main.py queue examples/incidents.json
python src/main.py show examples/incidents.json INC-1042
python src/main.py report examples/incidents.json --out reports/triage-report.json
```

The report command creates parent directories as needed and writes a new JSON report. The input file is never modified.

## Workflow modeled

1. Validate records and required fields.
2. Sort open records by calculated priority and age.
3. Review an individual record's impact, evidence, owner, and next step.
4. Export a concise handoff report for a shift or support meeting.

## Priority rules

- `critical`: production stopped or safety/quality impact is marked true.
- `high`: production is degraded or several work areas are affected.
- `normal`: all other open records.

The rule is a demonstrator, not a substitute for an organization's incident policy. The example data and names are invented.

## Design notes

- JSON is used as a portable input format.
- Validation errors identify the record and field that need correction.
- The core logic is separated from the CLI and uses only the Python standard library.
- Output includes the reason for the calculated priority to make decisions reviewable.

## Possible next steps

Add an agreed service taxonomy, a CSV import adapter, a persistent store, or integration contracts after requirements and data handling rules are defined.
