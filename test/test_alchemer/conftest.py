import json

import pytest

from parsons import Alchemer


@pytest.fixture
def alchemer(mocker):
    """An Alchemer connector with its ``surveygizmo`` client mocked.

    Alchemer wraps a ``surveygizmo.SurveyGizmo`` client (``self._client``); that client
    is the external boundary, so we patch it at its import site and program
    ``alchemer._client.api.survey.list`` / ``.surveyresponse.list`` per test.
    """
    mocker.patch("parsons.alchemer.alchemer.surveygizmo.SurveyGizmo")
    return Alchemer(api_token="fake-token", api_token_secret="fake-secret")


@pytest.fixture
def load(shared_datadir):
    """Load a canned surveygizmo response payload from the ``data/`` directory."""

    def _load(name: str):
        return json.loads((shared_datadir / f"{name}.json").read_text())

    return _load
