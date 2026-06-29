"""Port: loading authored ontologies. The core depends on this Protocol; a concrete
adapter (file-based today, database-backed later) satisfies it without the core ever
knowing which.
"""

from __future__ import annotations

from typing import Protocol

from recallos.core.domain.competency import Ontology


class OntologyRepository(Protocol):
    def get(self, domain: str, version: str | None = None) -> Ontology:
        """Return the ontology for `domain`. If `version` is given, the stored
        ontology must match it. Raises OntologyNotFoundError / OntologyValidationError.
        """
        ...

    def list_domains(self) -> list[str]:
        """Return the domains this repository can serve."""
        ...
