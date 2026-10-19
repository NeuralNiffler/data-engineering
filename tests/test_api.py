from unittest.mock import MagicMock

import pytest
import requests

import api


@pytest.fixture
def fake_get(monkeypatch):
    response = MagicMock()
    get = MagicMock(return_value=response)
    monkeypatch.setattr(api.requests, "get", get)
    return get, response


def test_get_status_calls_status_endpoint(fake_get):
    get, response = fake_get
    response.json.return_value = {"ready": True, "changeSeq": 42}

    assert api.get_status("host", "8102") == {"ready": True, "changeSeq": 42}
    get.assert_called_once_with("http://host:8102/api/status", timeout=10)


def test_get_change_seq_returns_int(fake_get):
    _, response = fake_get
    response.json.return_value = {"ready": True, "changeSeq": 42}

    assert api.get_change_seq("host", "8102") == 42


@pytest.mark.parametrize("payload, expected", [
    ({"ready": True}, True),
    ({"ready": False}, False),
    ({}, False),
])
def test_is_ready(fake_get, payload, expected):
    _, response = fake_get
    response.json.return_value = payload

    assert api.is_ready("host", "8102") is expected


@pytest.mark.parametrize("func", [api.get_status, api.is_ready, api.get_change_seq])
def test_http_error_is_raised(fake_get, func):
    _, response = fake_get
    response.raise_for_status.side_effect = requests.HTTPError("503")

    with pytest.raises(requests.HTTPError):
        func("host", "8102")
