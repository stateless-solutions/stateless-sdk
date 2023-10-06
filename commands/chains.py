from typer import Typer, Option, Argument
from rich.console import Console
from rich.table import Table
from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file
from gateway.domain.chains.dtos import ChainCreate, ChainUpdate

console = Console()
chains_app = Typer()


@chains_app.command("create")
def create_chain(
    config_file: str = Option(
        ..., help="The path to a JSON file with the chain creation data."
    )
):
    chain_create = parse_config_file(config_file, ChainCreate)
    response = make_request_with_api_key(
        "POST", V1Routes.CHAINS, chain_create.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 201:
        console.print(f"Successfully created chain {json_response['id']}")
    else:
        console.print(f"Error creating chain: {json_response['detail']}")


@chains_app.command("update")
def update_chain(
    chain_id: int = Argument(..., help="The ID of the chain to update."),
    config_file: str = Option(
        ..., help="The path to a JSON file with the update data."
    ),
):
    chain_update = parse_config_file(config_file, ChainUpdate)
    response = make_request_with_api_key(
        "PATCH", f"{V1Routes.CHAINS}/{chain_id}", chain_update.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 200:
        console.print(f"Successfully updated chain {json_response['id']}")
    else:
        console.print(f"Error updating chain: {json_response['detail']}")


@chains_app.command("get")
def get_chain(chain_id: int = Argument(..., help="The ID of the chain to get.")):
    response = make_request_with_api_key("GET", f"{V1Routes.CHAINS}/{chain_id}")

    json_response = response.json()

    if response.status_code == 200:
        console.print(json_response)  # Display the chain details
    else:
        console.print(f"Error getting chain: {json_response['detail']}")


@chains_app.command("list")
def list_chains():
    response = make_request_with_api_key("GET", V1Routes.LIST_CHAINS)

    json_response = response.json()

    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Name")
    # Add more columns as needed

    for item in json_response["items"]:
        table.add_row(item["id"], item["name"])  # Add more columns as needed

    console.print(table)


@chains_app.command("delete")
def delete_chain(chain_id: int = Argument(..., help="The ID of the chain to delete.")):
    response = make_request_with_api_key("DELETE", f"{V1Routes.CHAINS}/{chain_id}")

    if response.status_code == 204:
        console.print(f"Successfully deleted chain {chain_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting chain: {json_response['detail']}")
