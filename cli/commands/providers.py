from typer import Typer, Option, Argument
from rich.console import Console
from rich.table import Table
from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file

from cli.types.providers import ProviderCreate

console = Console()
providers_app = Typer()


@providers_app.command("create")
def create_provider(
    config_file: str = Option(
        ..., help="The path to a JSON file with the provider creation data."
    )
):
    provider_create = parse_config_file(config_file, ProviderCreate)
    response = make_request_with_api_key(
        "POST", V1Routes.PROVIDERS, provider_create.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 201:
        console.print(f"Successfully created provider {json_response['id']}")
    else:
        console.print(f"Error creating provider: {json_response['detail']}")


@providers_app.command("get")
def get_provider(
    provider_id: str = Argument(..., help="The ID of the provider to get.")
):
    response = make_request_with_api_key("GET", f"{V1Routes.PROVIDERS}/{provider_id}")

    json_response = response.json()

    if response.status_code == 200:
        console.print(json_response)  # Display the provider details
    else:
        console.print(f"Error getting provider: {json_response['detail']}")


@providers_app.command("list")
def list_providers():
    response = make_request_with_api_key("GET", V1Routes.LIST_PROVIDERS)

    json_response = response.json()

    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Name")
    # Add more columns as needed

    for item in json_response["items"]:
        table.add_row(item["id"], item["name"])  # Add more columns as needed

    console.print(table)


@providers_app.command("delete")
def delete_provider(
    provider_id: str = Argument(..., help="The ID of the provider to delete.")
):
    response = make_request_with_api_key(
        "DELETE", f"{V1Routes.PROVIDERS}/{provider_id}"
    )

    if response.status_code == 204:
        console.print(f"Successfully deleted provider {provider_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting provider: {json_response['detail']}")
