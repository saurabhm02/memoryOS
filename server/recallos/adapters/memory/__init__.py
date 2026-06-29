"""Memory engine adapters for the MemoryEngine port.

`FakeMemoryEngine` is the test double. `CogneeMemoryEngine` (the production engine) is
added in the phase that integrates Cognee.
"""

from .fake import FakeMemoryEngine

__all__ = ["FakeMemoryEngine"]
