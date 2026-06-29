"""End-to-end workflow validation suite.

Exercises the complete customer journey across the running platform —
authentication, case and account creation, document upload, the OCR →
classification → metadata → entity-resolution pipeline, timeline events,
task creation, and the Mission Control dashboard.

This package is a black-box system test: it talks to a *running* API over
HTTP and relies on a *running* worker to process the document pipeline.
See ``tests/e2e/README.md`` for how to run it locally and in CI.
"""
