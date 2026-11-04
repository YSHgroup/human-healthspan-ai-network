"""Separate AI platform package; no model workflows are implemented yet.

Three logically separated environments: `general` (General Platform AI), `scientist`
(Private AI Scientist) and `organization` (Organization-Specialized AI). They must not import
one another; any exchange goes through narrow, audited interfaces in `shared`/`governance`.
"""
