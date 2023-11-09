import os
import pytest
from unittest.mock import patch, Mock
import httpx
import respx

from pydantic import BaseModel

from cli.utils import (
    get_api_key_from_env,
    make_request_with_api_key,
    parse_config_file,
)


@patch.dict(os.environ, {"STATELESS_API_KEY": "my_api_key"})
def test_get_api_key_from_env_valid():
    assert get_api_key_from_env() == "my_api_key"


@patch.dict(os.environ, {})
def test_get_api_key_from_env_missing():
    with patch("cli.utils.secho") as mock_secho:
        assert get_api_key_from_env() is None
        mock_secho.assert_called_with(
            "API key not found in environment variables!", fg="red"
        )


@pytest.mark.parametrize(
    "method,url,data",
    [
        ("GET", "http://test.com", None),
        ("POST", "http://test.com", "some_data"),
        ("DELETE", "http://test.com", None),
        ("PATCH", "http://test.com", "some_data"),
        ("PUT", "http://test.com", "some_data"),
    ],
)
def test_make_request_with_api_key(method, url, data):
    with patch("cli.utils.get_api_key_from_env", return_value="dummy_api_key"):
        with respx.mock() as respx_instance:
            respx_route = respx_instance.route(method=method, url=url).mock(
                return_value=httpx.Response(200, json={"result": "ok"})
            )

            response = make_request_with_api_key(method, url, data)

            assert respx_route.called
            assert respx_route.call_count == 1

            request = respx_route.calls[0].request
            assert request.headers["X-API-KEY"] == "dummy_api_key"
            assert request.method == method

            if data is not None:
                assert request.read().decode("utf-8") == data

            # Check the response
            assert response.status_code == 200


class MockModel(BaseModel):
    @classmethod
    def model_validate(cls, json_data):
        return cls(**json_data)


@pytest.mark.parametrize(
    "file_path,model,expected_output",
    [
        (
            "fake_path",
            MockModel,
            MockModel(key="value"),
        ),
    ],
)
@patch("ujson.load")
@patch("builtins.open", new_callable=Mock)
def test_parse_config_file(mock_open, mock_load, file_path, model, expected_output):
    mock_load.return_value = {"key": "value"}

    mock_file = Mock()
    mock_file.__enter__ = Mock(return_value=mock_file)
    mock_file.__exit__ = Mock(return_value=None)
    mock_open.return_value = mock_file

    # When parse_config_file is called, it should return an instance of the model that contains the validated data
    assert parse_config_file(file_path, model) == expected_output


def test_make_request_with_api_key_invalid_method():
    with pytest.raises(ValueError):
        make_request_with_api_key("INVALID", "http://test.com")
