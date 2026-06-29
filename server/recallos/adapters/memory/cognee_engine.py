"""CogneeMemoryEngine — the production memory engine and RecallOS's core differentiator.

The only adapter that imports ``cognee``. It maps the platform's verbs onto Cognee
1.2.1's native async API:

- ``seed_graph``      -> ``remember`` the authored ontology into a per-user dataset
- ``ingest_evidence`` -> ``remember`` (permanent: add + cognify)
- ``derive_patterns`` -> ``improve`` (memify enrichment)
- ``narrate``         -> ``recall`` (graph-grounded answer)
- ``reset``           -> scoped ``forget(dataset=...)`` (never a global prune)

One Cognee dataset per user gives native isolation. The authored ontology is seeded so
Cognee's recall/reasoning have the competency structure as context; the deterministic
root-cause decision is made elsewhere from the canonical ontology, not from this engine.

Call ``init_cognee()`` (see ``cognee_runtime``) once at startup before using this engine.
"""

from __future__ import annotations

import re

import cognee

from recallos.core.application.ports import MemifyDelta
from recallos.core.domain.competency import Ontology
from recallos.core.domain.identity import UserScope
from recallos.core.domain.mastery import Observation

_UNSAFE = re.compile(r"[^a-zA-Z0-9_]")


class CogneeMemoryEngine:
    @staticmethod
    def _dataset(scope: UserScope) -> str:
        # One dataset per user; sanitized for a safe dataset name.
        return f"recallos_{_UNSAFE.sub('_', scope.user_id)}"

    async def provision(self, scope: UserScope) -> None:
        # Cognee creates the dataset lazily on first write, and (with access control
        # off) uses a default user; nothing is required up front.
        return None

    async def reset(self, scope: UserScope) -> None:
        try:
            await cognee.forget(dataset=self._dataset(scope))
        except (
            Exception
        ):  # noqa: BLE001 — dataset may not exist yet; reset is best-effort
            pass

    async def seed_graph(self, scope: UserScope, ontology: Ontology) -> None:
        lines = [f"Competency prerequisite map for {ontology.title}."]
        for src in sorted(ontology.graph.concepts):
            for tgt in sorted(ontology.graph.targets(src)):
                lines.append(f"'{src}' is a prerequisite of '{tgt}'.")
        await cognee.remember("\n".join(lines), dataset_name=self._dataset(scope))

    async def ingest_evidence(self, scope: UserScope, observation: Observation) -> None:
        card = (
            f"In a practice session the candidate scored {observation.score} out of 5 "
            f"on the concept '{observation.concept}'."
        )
        await cognee.remember(card, dataset_name=self._dataset(scope))

    async def derive_patterns(self, scope: UserScope) -> MemifyDelta:
        before_nodes, before_edges = await self._graph_size()
        await cognee.improve(dataset=self._dataset(scope))
        after_nodes, after_edges = await self._graph_size()
        return MemifyDelta(
            nodes_before=before_nodes,
            nodes_after=after_nodes,
            edges_before=before_edges,
            edges_after=after_edges,
        )

    async def narrate(self, scope: UserScope, prompt: str) -> str | None:
        try:
            results = await cognee.recall(prompt, datasets=[self._dataset(scope)])
        except Exception:  # noqa: BLE001 — narration is flavor, never load-bearing
            return None
        for item in results or []:
            text = _extract_text(item)
            if text:
                return text
        return None

    @staticmethod
    async def _graph_size() -> tuple[int, int]:
        """Best-effort node/edge counts for the Improve delta. Infrastructure-level
        read; returns (0, 0) if the engine doesn't expose it on this version."""
        try:
            from cognee.infrastructure.databases.graph.get_graph_engine import (
                get_graph_engine,
            )

            engine = await get_graph_engine()
            nodes, edges = await engine.get_graph_data()
            return len(nodes or []), len(edges or [])
        except Exception:  # noqa: BLE001 — metric only; never fail Improve over it
            return 0, 0


def _extract_text(item: object) -> str | None:
    for attr in ("answer", "text", "content"):
        value = getattr(item, attr, None)
        if isinstance(value, str) and value.strip():
            return value
    if isinstance(item, dict):
        for key in ("answer", "text", "content"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return None
