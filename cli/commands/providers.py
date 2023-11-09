import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file, handle_api_response
from cli.models.providers import ProviderCreate

console = Console()
providers_app = typer.Typer()


def prompt_for_provider_create() -> ProviderCreate:
    try:
        name = typer.prompt("Name")
        email = typer.prompt("Email")
        password = typer.prompt("Password", hide_input=True)
        payment_address = typer.prompt("Payment Address", default=None)
        return ProviderCreate(
            name=name, email=email, password=password, payment_address=payment_address
        )
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


@providers_app.command("create")
def create_provider(
    config_file: str = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the provider creation data.",
    )
):
    try:
        if config_file:
            provider_create = parse_config_file(config_file, ProviderCreate)
        else:
            provider_create = prompt_for_provider_create()
        response = make_request_with_api_key(
            "POST", V1Routes.PROVIDERS, provider_create.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@providers_app.command("get")
def get_provider(
    provider_id: str = typer.Argument(..., help="The ID of the provider to get.")
):
    try:
        response = make_request_with_api_key(
            "GET", f"{V1Routes.PROVIDERS}/{provider_id}"
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@providers_app.command("list")
def list_providers():
    try:
        response = make_request_with_api_key("GET", V1Routes.LIST_PROVIDERS)
        providers = response.json()["items"]
        table = Table(show_header=True, header_style="green")
        table.add_column("ID")
        table.add_column("Name")

        for item in providers:
            table.add_row(item["id"], item["name"])
        console.print(table)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@providers_app.command("delete")
def delete_provider(
    provider_id: str = typer.Argument(..., help="The ID of the provider to delete.")
):
    try:
        response = make_request_with_api_key(
            "DELETE", f"{V1Routes.PROVIDERS}/{provider_id}"
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()
