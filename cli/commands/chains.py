from typer import Typer, Option, Argument, prompt
from typing import Optional
from rich.console import Console
from rich.table import Table
from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file
from cli.models.chains import ChainCreate, ChainUpdate

console = Console()
chains_app = Typer()


@chains_app.command("create")
def create_chain(config_file: Optional[str] = Option(None, help="The path to a JSON file with the chain creation data.")):
    if config_file:
        chain_create = parse_config_file(config_file, ChainCreate)
    else:
        # Interactive Prompts for Chain Creation
        chain_id = prompt("Enter the ID of the chain", type=int)
        name = prompt("Enter the name of the chain")

        chain_create = ChainCreate(chain_id=chain_id, name=name)
        
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
    chain_id: Optional[int] = Argument(None, help="The ID of the chain to update."),
    config_file: Optional[str] = Option(None, help="The path to a JSON file with the update data.")
):
    if chain_id is None:
        chain_id = prompt("Enter the ID of the chain to update", type=int)

    if config_file:
        chain_update = parse_config_file(config_file, ChainUpdate)
    else:
        name = prompt("Enter the updated name of the chain", default=None)

        chain_update = ChainUpdate(name=name)
        
    response = make_request_with_api_key(
        "PATCH", f"{V1Routes.CHAINS}/{chain_id}", chain_update.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 200:
        console.print(f"Successfully updated chain {json_response['id']}")
    else:
        console.print(f"Error updating chain: {json_response['detail']}")


@chains_app.command("get")
def get_chain(chain_id: Optional[int] = Argument(None, help="The ID of the chain to get.")):
    if chain_id is None:
        chain_id = prompt("Enter the ID of the chain to get", type=int)
        
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
def delete_chain(chain_id: Optional[int] = Argument(None, help="The ID of the chain to delete.")):
    if chain_id is None:
        chain_id = prompt("Enter the ID of the chain to delete", type=int)
        
    response = make_request_with_api_key("DELETE", f"{V1Routes.CHAINS}/{chain_id}")

    if response.status_code == 204:
        console.print(f"Successfully deleted chain {chain_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting chain: {json_response['detail']}")
