"""Provider-agnostic OIDC JWT verification.

Validates a bearer token's signature against the issuer's JWKS (RS256/ES256) plus
issuer/audience/expiry, and returns a `Principal`. Works with Supabase, Keycloak,
Authentik, Auth0, Clerk — any standard OIDC provider — selected purely by config.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import jwt
from jwt import PyJWKClient

from recallos.core.domain.identity import Principal


class AuthError(Exception):
    """Authentication failed: missing, malformed, expired, or untrusted token."""


class JwtPrincipalVerifier:
    def __init__(
        self,
        *,
        issuer: str,
        audience: str,
        jwks_url: str | None = None,
        algorithms: Sequence[str] = ("RS256", "ES256"),
        leeway: int = 10,
        key_resolver: Callable[[str], object] | None = None,
    ) -> None:
        self._issuer = issuer
        self._audience = audience
        self._algorithms = list(algorithms)
        self._leeway = leeway
        # `key_resolver` lets tests inject a signing key without a network JWKS.
        self._key_resolver = key_resolver
        self._jwks = PyJWKClient(jwks_url) if jwks_url and key_resolver is None else None

    def verify(self, token: str) -> Principal:
        try:
            key = (
                self._key_resolver(token)
                if self._key_resolver is not None
                else self._jwks.get_signing_key_from_jwt(token).key  # type: ignore[union-attr]
            )
            options = {"require": ["exp", "sub"], "verify_aud": bool(self._audience)}
            kwargs: dict[str, object] = {
                "algorithms": self._algorithms,
                "leeway": self._leeway,
                "options": options,
            }
            if self._audience:
                kwargs["audience"] = self._audience
            if self._issuer:
                kwargs["issuer"] = self._issuer
            claims = jwt.decode(token, key, **kwargs)  # type: ignore[arg-type]
        except Exception as exc:  # noqa: BLE001 — any failure is an auth failure
            raise AuthError(str(exc)) from exc

        subject = claims.get("sub")
        if not subject:
            raise AuthError("token is missing a subject")
        return Principal(subject=str(subject), email=claims.get("email"))
