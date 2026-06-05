# Update System

Use this folder for reusable update discipline.

For each upgrade, create a private run record under `.local_runs/<run_id>/updates/` with:

- intent
- files or modules changed
- input before change
- output after change
- verification performed
- known risks

Commit only generic templates and system rules here.
