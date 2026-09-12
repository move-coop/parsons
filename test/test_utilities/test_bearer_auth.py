"""Tests for :class:`~parsons.utilities.bearer_auth.BearerAuth`."""

from __future__ import annotations

import secrets

import pytest
import requests

from parsons.utilities.bearer_auth import BearerAuth


@pytest.fixture
def bearer_auth() -> BearerAuth:
    """Fixture for creating a BearerAuth object."""
    api_token = secrets.token_hex(64)
    return BearerAuth(api_token)


def test_auth_init() -> None:
    """Test that the auth object is initialized with the supplied API key."""
    api_token = secrets.token_hex(64)
    auth = BearerAuth(api_token)
    assert auth.api_key == api_token


def test_auth_strips() -> None:
    """Test that the auth object is initialized with the supplied API key, with leading and trailing whitespace removed."""
    api_token = secrets.token_hex(64)
    auth = BearerAuth(f" {api_token} ")
    assert auth.api_key == api_token


def test_auth_eq() -> None:
    """Test that instances of auth objects with the same API key can be compared for equality."""
    api_token1 = secrets.token_hex(64)
    auth1_1 = BearerAuth(api_token1)
    auth1_2 = BearerAuth(api_token1)
    assert auth1_1 == auth1_2

    api_token2 = secrets.token_hex(64)
    auth2_1 = BearerAuth(api_token2)
    assert auth1_1 != auth2_1


def test_auth_hash(bearer_auth: BearerAuth) -> None:
    """Test that auth objects are hashable based on their API key and can be used as dictionary keys."""
    assert hash(bearer_auth) == hash(bearer_auth.api_key)


def test_auth_repr(bearer_auth: BearerAuth) -> None:
    """Test that auth objects include the API key in their repr."""
    assert bearer_auth.api_key in repr(bearer_auth)


def test_auth_call(bearer_auth: BearerAuth) -> None:
    """Test that calling an auth object with a request adds the authorization header."""
    req = requests.Request(url="https://example.com")
    req = req.prepare()
    bearer_auth(req)
    assert req.headers["authorization"] == f"Bearer {bearer_auth.api_key}"


def test_auth_call_does_not_clear_headers(bearer_auth: BearerAuth) -> None:
    """Test that calling an auth object with a request adds the authorization header to existing headers."""
    req = requests.Request(url="https://example.com", headers={"X-Test": "test"})
    req = req.prepare()
    bearer_auth(req)
    assert req.headers["authorization"] == f"Bearer {bearer_auth.api_key}"
    assert req.headers["X-Test"] == "test"
