import pytest
from typer.testing import CliRunner
from cli.commands.users import users_app, prompt_for_user_create
from unittest.mock import patch
from cli.models.users import UserCreate
from uuid import uuid4
import ujson as json
import respx
from httpx import Response
from cli.routes import V1Routes

runner = CliRunner()


@pytest.fixture
def mock_env_api_key(monkeypatch):
    monkeypatch.setenv("STATELESS_API_KEY", "test_api_key")


@pytest.fixture
def mock_parse_config_file(monkeypatch, user_create_data):
    def mock_return(user_create_data):
        return user_create_data

    monkeypatch.setattr("cli.utils.parse_config_file", mock_return)


@pytest.fixture
def user_create_data():
    return UserCreate(
        id=uuid4(),
        oauth_id="test_oauth_id",
        username="test_username",
        name="Test Name",
        email="test@example.com",
    )


@pytest.mark.parametrize(
    "oauth_id,username,name,email",
    [
        ("test_oauth_id_1", "test_username_1", "Test Name 1", "test1@example.com"),
        ("test_oauth_id_2", "test_username_2", None, None),  # Testing optional fields
        ("test_oauth_id_3", "test_username_3", "Test Name 3", "test3@example.com"),
    ],
)
def test_prompt_for_user_create(oauth_id, username, name, email):
    with patch("typer.prompt") as mock_prompt:
        mock_prompt.side_effect = [oauth_id, username, name, email]
        user_create = prompt_for_user_create()
        assert user_create.oauth_id == oauth_id
        assert user_create.username == username
        assert user_create.name == name
        assert user_create.email == email


@pytest.mark.parametrize(
    "status_code,expected_exit_code", [(200, 0), (400, 1), (500, 1)]
)
def test_create_user_with_config(
    status_code,
    expected_exit_code,
    mock_env_api_key,
    mock_parse_config_file,
):
    # Mock the POST request
    with respx.mock() as respx_instance:
        respx_instance.post(V1Routes.USERS).mock(
            return_value=Response(
                status_code,
                json={"result": "success"}
                if status_code == 200
                else {"error": "failure"},
            )
        )

        # Invoke the CLI runner
        result = runner.invoke(
            users_app, ["create", "--config-file", "path/to/config.json"]
        )
        assert result.exit_code == expected_exit_code
        if status_code == 200:
            assert "success" in result.stdout
        else:
            assert "failure" in result.stdout


# Other tests remain unchanged


@pytest.mark.parametrize(
    "status_code,expected_exit_code,expected_num_users",
    [(200, 0, 2), (500, 1, 0)],
)
def test_list_users(
    status_code, expected_exit_code, expected_num_users, mock_env_api_key
):
    # Mock the GET request
    with respx.mock() as respx_instance:
        respx_instance.get(V1Routes.LIST_USERS).mock(
            return_value=Response(
                status_code,
                json={
                    "items": [
                        {"id": "1", "name": "User One"},
                        {"id": "2", "name": "User Two"},
                    ]
                }
                if status_code == 200
                else {"error": "internal server error"},
            )
        )
        # Invoke the CLI runner
        result = runner.invoke(users_app, ["list"])
        assert result.exit_code == expected_exit_code
        if status_code == 200:
            response_data = json.loads(result.stdout)
            assert len(response_data["items"]) == expected_num_users
        else:
            assert "internal server error" in result.stdout


@pytest.mark.parametrize(
    "user_id,status_code,expected_exit_code",
    [("123", 204, 0), ("does_not_exist", 404, 1), ("123", 500, 1)],
)
def test_delete_user(user_id, status_code, expected_exit_code, mock_env_api_key):
    # Mock the DELETE request
    with respx.mock() as respx_instance:
        respx_instance.delete(f"{V1Routes.USERS}/{user_id}").mock(
            return_value=Response(
                status_code,
                json={"result": "user deleted"}
                if status_code == 204
                else {"error": "user not found"},
            )
        )
        # Invoke the CLI runner
        result = runner.invoke(users_app, ["delete", user_id])
        assert result.exit_code == expected_exit_code
        if status_code == 204:
            assert "user deleted" in result.stdout
        else:
            assert "user not found" in result.stdout
