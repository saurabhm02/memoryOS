"""Authentication adapters (edge concern). Provider-agnostic OIDC JWT verification —
the backend trusts only standard JWTs validated against a configured JWKS, never a
client-supplied identity. Swap providers by configuration alone.
"""

from .jwt_verifier import AuthError, JwtPrincipalVerifier

__all__ = ["AuthError", "JwtPrincipalVerifier"]
