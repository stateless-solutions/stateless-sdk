from typer import Typer, Option, Argument
from rich.console import Console
from rich.table import Table
from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file
from cli.models.api_keys import APIKeyUpdate, APIKeyCreate

console = Console()
api_keys_app = Typer()


@api_keys_app.command("create")
def create_api_key(
    config_file: str = Option(
        ..., help="The path to a JSON file with the API key creation data."
    )
):
    api_key_create = parse_config_file(config_file, APIKeyCreate)
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
    api_key_id: str = Argument(..., help="The UUID of the API key to update."),
    config_file: str = Option(
        ..., help="The path to a JSON file with the update data."
    ),
):
    api_key_update = parse_config_file(config_file, APIKeyUpdate)
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
    api_key_id: str = Argument(..., help="The UUID of the API key to get.")
):
    response = make_request_with_api_key("GET", f"{V1Routes.API_KEYS}/{api_key_id}")

    json_response = response.json()

    if response.status_code == 200:
        console.print(json_response)
    else:
        console.print(f"Error getting API key: {json_response['detail']}")


@api_keys_app.command("list")
def list_api_keys():
    response = make_request_with_api_key("GET", V1Routes.API_KEYS)
    json_response = response.json()

    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Name")

    for item in json_response["items"]:
        table.add_row(item["id"], item["name"])

    console.print(table)


@api_keys_app.command("delete")
def delete_api_key(
    api_key_id: str = Argument(..., help="The UUID of the API key to delete.")
):
    response = make_request_with_api_key("DELETE", f"{V1Routes.API_KEYS}/{api_key_id}")

    if response.status_code == 204:
        console.print(f"Successfully deleted API key {api_key_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting API key: {json_response['detail']}")
