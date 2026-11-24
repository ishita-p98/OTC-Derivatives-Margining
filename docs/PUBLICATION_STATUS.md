# Publication status

This branch contains the reorganized and anonymized presentation of the collaborative university project.

## Included

- Four focused notebooks for the assignment's main themes, plus the original submitted notebook archived for provenance.
- Reusable simulation engine in `src/otc_margining.py` and a deterministic analysis runner.
- Seven regenerated PNG charts and four lightweight SVG summary charts.
- Scenario tables in CSV and JSON.
- Five-page technical summary PDF, generated from the corrected simulation outputs.
- Methodology, source review, model audit, results and contribution notes.
- Automated integrity tests and a GitHub Actions workflow that regenerates the analysis outputs and report.

## Exclusions

- The original assignment and group report PDFs are not included because the report contains student names and student identifiers.
- No external market-data files, licensed CSVs or Excel workbooks are included.
- No student numbers or full group roster are republished.
- No original Git history from other project repositories is imported.

## Validation scope

The GitHub Actions workflow passed the project checks, regenerated the simulation outputs and figures, and successfully built the five-page PDF. The checks cover deterministic model invariants, notebook JSON structure and reproducible execution of the analysis script.

This does not make the model an empirically calibrated or regulatory-grade risk engine. It remains a stylized educational simulation with the limitations documented in `docs/MODEL_AUDIT.md` and `docs/SIMULATION_RESULTS.md`.

No open-source licence is granted. Reuse permissions should be agreed by the relevant contributors.
