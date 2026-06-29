"""File-backed `OntologyRepository`: loads one YAML file per domain.

Files are named `{domain}.yaml` and validated on load (DAG acyclicity and no
dangling edges come from `PrereqGraph.from_mapping`). Results are cached. A
database-backed repository can replace this later behind the same port; multi-file
version resolution is deferred until versioning actually ships.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from recallos.core.domain.competency import Ontology, PrereqGraph
from recallos.core.domain.errors import (
    OntologyNotFoundError,
    OntologyValidationError,
)


class FileOntologyRepository:
    def __init__(self, directory: str | Path) -> None:
        self._dir = Path(directory)
        self._cache: dict[tuple[str, str | None], Ontology] = {}

    def get(self, domain: str, version: str | None = None) -> Ontology:
        cache_key = (domain, version)
        if cache_key in self._cache:
            return self._cache[cache_key]

        path = self._dir / f"{domain}.yaml"
        if not path.exists():
            raise OntologyNotFoundError(
                f"no ontology file for domain {domain!r} at {path}"
            )

        ontology = _parse_ontology(path)
        if version is not None and ontology.version != version:
            raise OntologyValidationError(
                f"domain {domain!r} is version {ontology.version}, "
                f"requested {version!r}"
            )

        self._cache[cache_key] = ontology
        return ontology

    def list_domains(self) -> list[str]:
        return sorted(p.stem for p in self._dir.glob("*.yaml"))


def _parse_ontology(path: Path) -> Ontology:
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise OntologyValidationError(f"{path.name}: invalid YAML: {exc}") from exc

    if not isinstance(raw, dict):
        raise OntologyValidationError(f"{path.name}: top-level YAML must be a mapping")

    try:
        domain = str(raw["domain"])
        version = str(raw["version"])
        title = str(raw["title"])
        weak_threshold = float(raw["weak_threshold"])
        concepts = raw["concepts"]
    except KeyError as exc:
        raise OntologyValidationError(f"{path.name}: missing required key {exc}") from exc

    if not isinstance(concepts, list):
        raise OntologyValidationError(f"{path.name}: 'concepts' must be a list")

    mapping: dict[str, list[str]] = {}
    for entry in concepts:
        try:
            name = str(entry["name"])
        except (KeyError, TypeError) as exc:
            raise OntologyValidationError(
                f"{path.name}: every concept needs a 'name'"
            ) from exc
        if name in mapping:
            raise OntologyValidationError(f"{path.name}: duplicate concept {name!r}")
        mapping[name] = [str(t) for t in entry.get("prereq_of", [])]

    graph = PrereqGraph.from_mapping(mapping)
    return Ontology(
        domain=domain,
        version=version,
        title=title,
        weak_threshold=weak_threshold,
        graph=graph,
    )
