import typer
from typing import Optional
from datetime import datetime
from pydantic import UUID4, ValidationError
from rich.console import Console
from rich.table import Table
from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file, handle_api_response
from cli.models.api_keys import APIKeyUpdate, APIKeyCreate

console = Console()
api_keys_app = typer.Typer()


def prompt_for_api_key_create() -> APIKeyCreate:
    try:
        account_id = typer.prompt("Account ID", type=UUID4)
        name = typer.prompt("API Key Name")
        prefix = typer.prompt("API Key Prefix", default=None)
        expires_at_str = typer.prompt(
            "Expiration datetime (YYYY-MM-DDTHH:MM:SS)", default=None
        )
        expires_at = datetime.fromisoformat(expires_at_str) if expires_at_str else None
        return APIKeyCreate(
            account_id=account_id, name=name, prefix=prefix, expires_at=expires_at
        )
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


def prompt_for_api_key_update() -> APIKeyUpdate:
    try:
        name = typer.prompt("API Key Name", default=None)
        prefix = typer.prompt("API Key Prefix", default=None)
        expires_at_str = typer.prompt(
            "Expiration datetime (YYYY-MM-DDTHH:MM:SS)", default=None
        )
        expires_at = datetime.fromisoformat(expires_at_str) if expires_at_str else None
        return APIKeyUpdate(name=name, prefix=prefix, expires_at=expires_at)
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


@api_keys_app.command("create")
def create_api_key(
    config_file: Optional[str] = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the API key creation data.",
    )
):
    try:
        if config_file:
            api_key_create = parse_config_file(config_file, APIKeyCreate)
        else:
            api_key_create = prompt_for_api_key_create()
        response = make_request_with_api_key(
            "POST", V1Routes.API_KEYS, api_key_create.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@api_keys_app.command("update")
def update_api_key(
    api_key_id: Optional[str] = typer.Argument(
        None, help="The UUID of the API key to update."
    ),
    config_file: Optional[str] = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the update data.",
    ),
):
    try:
        api_key_id = api_key_id or typer.prompt("API Key ID", type=UUID4)
        if config_file:
            api_key_update = parse_config_file(config_file, APIKeyUpdate)
        else:
            api_key_update = prompt_for_api_key_update()
        response = make_request_with_api_key(
            "PATCH", f"{V1Routes.API_KEYS}/{api_key_id}", api_key_update.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@api_keys_app.command("get")
def get_api_key(
    api_key_id: Optional[str] = typer.Argument(
        None, help="The UUID of the API key to get."
    )
):
    try:
        api_key_id = api_key_id or typer.prompt("API Key ID", type=UUID4)
        response = make_request_with_api_key("GET", f"{V1Routes.API_KEYS}/{api_key_id}")
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@api_keys_app.command("list")
def list_api_keys():
    try:
        response = make_request_with_api_key("GET", V1Routes.API_KEYS)
        json_response = response.json()
        if response.status_code == 200:
            table = Table(show_header=True, header_style="bold green")
            table.add_column("ID", style="dim")
            table.add_column("Name")
            table.add_column("Prefix")
            table.add_column("Expires At")
            for item in json_response["items"]:
                expires_at = (
                    item["expires_at"].strftime("%Y-%m-%d %H:%M:%S")
                    if item["expires_at"]
                    else "Never"
                )
                table.add_row(item["id"], item["name"], item["prefix"], expires_at)
            console.print(table)
        else:
            console.print(
                f"Error retrieving API keys: {json_response['detail']}",
                style="bold red",
            )
            raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@api_keys_app.command("delete")
def delete_api_key(
    api_key_id: Optional[str] = typer.Argument(
        None, help="The UUID of the API key to delete."
    )
):
    try:
        api_key_id = api_key_id or typer.prompt("API Key ID", type=UUID4)
        response = make_request_with_api_key(
            "DELETE", f"{V1Routes.API_KEYS}/{api_key_id}"
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()
