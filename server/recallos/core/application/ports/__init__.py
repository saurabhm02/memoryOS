"""Ports — abstract interfaces the core depends on. Adapters implement them; the
core never imports an adapter. New ports are introduced only when a real consumer
and a real implementation exist for them.
"""

from .answer_scorer import AnswerScorer
from .evidence_ledger import EvidenceLedger
from .memory_engine import MemifyDelta, MemoryEngine
from .ontology_repository import OntologyRepository
from .user_repository import UserRepository

__all__ = [
    "AnswerScorer",
    "EvidenceLedger",
    "MemifyDelta",
    "MemoryEngine",
    "OntologyRepository",
    "UserRepository",
]
