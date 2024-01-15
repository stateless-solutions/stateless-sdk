from typing import Optional

from rich.console import Console
from rich.table import Table
from typer import Argument, Option, Typer, prompt

from ..models.providers import ProviderCreate
from ..routes import V1Routes
from ..utils import make_request_with_api_key, parse_config_file, provider_guard

console = Console()
providers_app = Typer()

@providers_app.command("create")
def create_provider(
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the provider creation data.",
    ),
):
    provider_guard()
    
    if config_file:
        provider_create = parse_config_file(config_file, ProviderCreate)
    else:
        oauth_id = prompt("Enter OAuth2 Unique Identifier")
        email = prompt("Enter Email Address", default=None)
        name = prompt("Enter Name", default=None)
        username = prompt("Enter Username")
        payment_address = prompt("Enter Payment Address", default=None)

        provider_create = ProviderCreate(
            oauth_id=oauth_id,
            email=email,
            name=name,
            username=username,
            payment_address=payment_address,
        )

    response = make_request_with_api_key(
        "POST", V1Routes.PROVIDERS, provider_create.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 201:
        console.print(f"Successfully created provider {json_response['id']}")
    else:
        console.print(f"Error creating provider: {json_response['detail']}")


@providers_app.command("view")
def get_provider(
    provider_id: Optional[str] = Argument(None, help="The ID of the provider to view.")
):
    provider_guard()
    
    if not provider_id:
        provider_id = prompt("Enter the ID of the provider to view")

    response = make_request_with_api_key("GET", f"{V1Routes.PROVIDERS}/{provider_id}")

    json_response = response.json()

    if response.status_code == 200:
        console.print(json_response)
    else:
        console.print(f"Error getting provider: {json_response['detail']}")


@providers_app.command("list")
def list_providers():
    response = make_request_with_api_key("GET", V1Routes.LIST_PROVIDERS)

    json_response = response.json()

    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Name")

    for item in json_response["items"]:
        table.add_row(item["id"], item["name"])

    console.print(table)


@providers_app.command("delete")
def delete_provider(
    provider_id: Optional[str] = Argument(
        None, help="The ID of the provider to delete."
    ),
):
    provider_guard()
    if not provider_id:
        provider_id = prompt("Enter the ID of the provider to delete")

    response = make_request_with_api_key(
        "DELETE", f"{V1Routes.PROVIDERS}/{provider_id}"
    )

    if response.status_code == 204:
        console.print(f"Successfully deleted provider {provider_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting provider: {json_response['detail']}")
