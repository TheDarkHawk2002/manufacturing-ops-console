# Internal implementation plan (not for GitHub)

1. Keep the project synthetic and independent from any employer systems.
2. Model a small incident schema: identity, application, site, timestamp, state, impact, safety/quality flag, evidence, owner, next step.
3. Validate input before applying business rules; reject ambiguous or malformed records with field-level messages.
4. Calculate a transparent priority using deterministic rules and explain the reason in every output.
5. Provide a queue view, individual case view, and non-overwriting JSON handoff report.
6. Document assumptions, limitations, and plausible future adapters without claiming MES, SAP, or production experience.
