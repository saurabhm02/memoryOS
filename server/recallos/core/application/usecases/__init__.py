"""Use-cases: the application's verbs, orchestrating pure domain logic over ports.
One class per verb, each independently testable with the fake memory engine.
"""

from .build_competency_graph import BuildCompetencyGraph
from .diagnose_session import DiagnoseSession
from .forget_concept import ForgetConcept
from .improve_memory import ImproveMemory
from .provision_scope import ProvisionScope
from .remember_observation import RememberObservation, RememberResult
from .reset_learner_memory import ResetLearnerMemory
from .score_answer import ScoreAnswer, ScoreAnswerResult

__all__ = [
    "BuildCompetencyGraph",
    "DiagnoseSession",
    "ForgetConcept",
    "ImproveMemory",
    "ProvisionScope",
    "RememberObservation",
    "RememberResult",
    "ResetLearnerMemory",
    "ScoreAnswer",
    "ScoreAnswerResult",
]
