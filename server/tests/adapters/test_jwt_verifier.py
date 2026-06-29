import time

import jwt as pyjwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from recallos.adapters.auth import AuthError, JwtPrincipalVerifier

_ISSUER = "https://issuer.example"
_AUDIENCE = "authenticated"


def _keypair():
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return private, private.public_key()


def _token(private, claims: dict) -> str:
    return pyjwt.encode(claims, private, algorithm="RS256")


def _verifier(public):
    return JwtPrincipalVerifier(
        issuer=_ISSUER, audience=_AUDIENCE, key_resolver=lambda _token: public
    )


def _claims(**overrides) -> dict:
    base = {
        "sub": "user-123",
        "email": "a@b.com",
        "iss": _ISSUER,
        "aud": _AUDIENCE,
        "exp": int(time.time()) + 3600,
    }
    base.update(overrides)
    return base


def test_verifies_valid_token_and_extracts_principal():
    private, public = _keypair()
    principal = _verifier(public).verify(_token(private, _claims()))
    assert principal.subject == "user-123"
    assert principal.email == "a@b.com"


def test_rejects_expired_token():
    private, public = _keypair()
    token = _token(private, _claims(exp=int(time.time()) - 10))
    with pytest.raises(AuthError):
        _verifier(public).verify(token)


def test_rejects_wrong_audience():
    private, public = _keypair()
    token = _token(private, _claims(aud="someone-else"))
    with pytest.raises(AuthError):
        _verifier(public).verify(token)


def test_rejects_wrong_issuer():
    private, public = _keypair()
    token = _token(private, _claims(iss="https://evil.example"))
    with pytest.raises(AuthError):
        _verifier(public).verify(token)


def test_rejects_token_signed_by_another_key():
    private, _ = _keypair()
    _, other_public = _keypair()
    token = _token(private, _claims())
    with pytest.raises(AuthError):
        _verifier(other_public).verify(token)
