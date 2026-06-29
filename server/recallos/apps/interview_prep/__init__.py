"""Interview prep — the first RecallOS app (v1). Backend-Engineer interview
preparation. Owns its ontology data under `ontologies/`.
"""

from pathlib import Path

ONTOLOGY_DIR = Path(__file__).resolve().parent / "ontologies"
"""Directory of this app's authored ontologies, for wiring a FileOntologyRepository."""
