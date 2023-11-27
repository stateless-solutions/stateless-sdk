from typer import Typer, Option, Argument, prompt
from typing import Optional
from rich.console import Console
from rich.table import Table
from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file
from datetime import datetime
from cli.models.api_keys import APIKeyUpdate, APIKeyCreate

console = Console()
api_keys_app = Typer()


@api_keys_app.command("create")
def create_api_key(
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the user creation data.",
    ),
):
    if config_file:
        api_key_create = parse_config_file(config_file, APIKeyCreate)
    else:
        # Interactive Prompts for API Key Creation
        account_id = prompt("Enter the account ID", type=str, default=None)
        name = prompt("Enter the name of the API key")
        prefix = prompt("Enter the prefix of the API key", default=None)
        expires_at = prompt(
            "Enter the expiration datetime of the API key (YYYY-MM-DD HH:MM:SS)",
            default=None,
        )
        expires_at = (
            datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") if expires_at else None
        )

        api_key_create = APIKeyCreate(
            account_id=account_id, name=name, prefix=prefix, expires_at=expires_at
        )

    response = make_request_with_api_key(
        "POST", V1Routes.API_KEYS, api_key_create.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 201:
        console.print(f"Successfully created API key {json_response['key']}")
    else:
        console.print(f"Error creating API key: {json_response['detail']}")


@api_keys_app.command("update")
def update_api_key(
    api_key_id: Optional[str] = Argument(
        None, help="The UUID of the API key to update."
    ),
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the update data.",
    ),
):
    if not api_key_id:
        api_key_id = prompt("Enter the UUID of the API key to update")

    if config_file:
        api_key_update = parse_config_file(config_file, APIKeyUpdate)
    else:
        # Interactive Prompts for API Key Update
        name = prompt("Enter the updated name of the API key", default=None)
        prefix = prompt("Enter the updated prefix of the API key", default=None)
        expires_at = prompt(
            "Enter the updated expiration datetime of the API key (YYYY-MM-DD HH:MM:SS)",
            default=None,
        )
        expires_at = (
            datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") if expires_at else None
        )

        api_key_update = APIKeyUpdate(name=name, prefix=prefix, expires_at=expires_at)

    response = make_request_with_api_key(
        "PATCH", f"{V1Routes.API_KEYS}/{api_key_id}", api_key_update.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 200:
        console.print(f"Successfully updated API key {json_response['id']}")
    else:
        console.print(f"Error updating API key: {json_response['detail']}")


@api_keys_app.command("get")
def get_api_key(
    api_key_id: Optional[str] = Argument(None, help="The UUID of the API key to get.")
):
    if not api_key_id:
        api_key_id = prompt("Enter the UUID of the API key to get")

    response = make_request_with_api_key("GET", f"{V1Routes.API_KEYS}/{api_key_id}")

    json_response = response.json()

    if response.status_code == 200:
        console.print(json_response)
    else:
        console.print(f"Error getting API key: {json_response['detail']}")


@api_keys_app.command("list")
def list_api_keys():
    response = make_request_with_api_key("GET", V1Routes.LIST_API_KEYS)
    json_response = response.json()

    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Name")

    for item in json_response["items"]:
        table.add_row(item["id"], item["name"])

    console.print(table)


@api_keys_app.command("delete")
def delete_api_key(
    api_key_id: Optional[str] = Argument(
        None, help="The UUID of the API key to delete."
    ),
):
    if not api_key_id:
        api_key_id = prompt("Enter the UUID of the API key to delete")

    response = make_request_with_api_key("DELETE", f"{V1Routes.API_KEYS}/{api_key_id}")

    if response.status_code == 204:
        console.print(f"Successfully deleted API key {api_key_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting API key: {json_response['detail']}")
