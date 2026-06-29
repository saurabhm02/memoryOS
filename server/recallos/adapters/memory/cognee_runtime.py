"""Configure and initialize the Cognee runtime — the production memory engine.

Infrastructure only. Wires Cognee 1.2.1 to local stores (SQLite + Kuzu + LanceDB under
``server/.cognee``) and to the configured LLM/embedding provider (Gemini). Call
``init_cognee()`` once at process startup before using ``CogneeMemoryEngine``.

Verified working config (see docs/PRODUCTION_ARCHITECTURE.md §5.0.1):
LLM ``gemini/gemini-2.5-flash``, embeddings ``gemini/gemini-embedding-001`` @ 3072,
graph ``kuzu`` (downloads a JSON extension on first init — needs egress / pre-install).
"""

from __future__ import annotations

import os
from pathlib import Path

from recallos.config import settings

_initialized = False


async def init_cognee() -> None:
    """Idempotent process-level setup. Safe to call once at startup."""
    global _initialized
    if _initialized:
        return

    import cognee
    from cognee.low_level import setup as cognee_low_level_setup

    key = settings.resolved_gemini_key()
    if key:
        # LiteLLM reads GEMINI_API_KEY from the environment for gemini/* models.
        os.environ["GEMINI_API_KEY"] = key
    os.environ["ENABLE_BACKEND_ACCESS_CONTROL"] = str(
        settings.enable_backend_access_control
    ).lower()

    cognee.config.system_root_directory(str(Path(settings.cognee_system_dir).resolve()))
    cognee.config.data_root_directory(str(Path(settings.cognee_data_dir).resolve()))
    cognee.config.set_relational_db_config({"db_provider": "sqlite"})
    cognee.config.set_graph_db_config(
        {"graph_database_provider": settings.graph_provider}
    )
    cognee.config.set_vector_db_config({"vector_db_provider": "lancedb"})
    cognee.config.set_llm_provider(settings.llm_provider)
    cognee.config.set_llm_model(settings.llm_model)
    cognee.config.set_llm_api_key(key)
    cognee.config.set_embedding_provider(settings.embedding_provider)
    cognee.config.set_embedding_model(settings.embedding_model)
    cognee.config.set_embedding_dimensions(settings.embedding_dimensions)

    await cognee_low_level_setup()
    _initialized = True
