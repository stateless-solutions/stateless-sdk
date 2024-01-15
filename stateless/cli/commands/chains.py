from typing import Optional

from rich.console import Console
from rich.table import Table
from typer import Argument, Option, Typer, prompt

from ..models.chains import ChainCreate, ChainUpdate
from ..routes import V1Routes
from ..utils import make_request_with_api_key, parse_config_file

console = Console()
chains_app = Typer()


@chains_app.command("create")
def create_chain(
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the chain creation data.",
    ),
):
    if config_file:
        chain_create = parse_config_file(config_file, ChainCreate)
    else:
        chain_id = prompt("Enter the ID of the chain", type=int)
        name = prompt("Enter the name of the chain")

        chain_create = ChainCreate(chain_id=chain_id, name=name)

    try:
        response = make_request_with_api_key(
            "POST", V1Routes.CHAINS, chain_create.model_dump_json()
        )

        json_response = response.json()

        if response.status_code == 201:
            console.print(f"Successfully created chain {json_response['id']}")

    except Exception:
        return

@chains_app.command("update")
def update_chain(
    chain_id: Optional[int] = Argument(None, help="The ID of the chain to update."),
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the update data.",
    ),
):
    if chain_id is None:
        chain_id = prompt("Enter the ID of the chain to update", type=int)

    if config_file:
        chain_update = parse_config_file(config_file, ChainUpdate)
    else:
        name = prompt("Enter the updated name of the chain", default=None)

        chain_update = ChainUpdate(name=name)

    try:
        response = make_request_with_api_key(
            "PATCH", f"{V1Routes.CHAINS}/{chain_id}", chain_update.model_dump_json()
        )

        json_response = response.json()

        if response.status_code == 200:
            console.print(f"Successfully updated chain {json_response['id']}")

    except Exception:
        return


@chains_app.command("view")
def get_chain(
    chain_id: Optional[int] = Argument(None, help="The ID of the chain to view.")
):
    if chain_id is None:
        chain_id = prompt("Enter the ID of the chain to view", type=int)

    try:
        response = make_request_with_api_key("GET", f"{V1Routes.CHAINS}/{chain_id}")

        json_response = response.json()

        if response.status_code == 200:
            table = Table(show_header=True, header_style="green")
            table.add_column("Chain ID")
            table.add_column("Name")

            table.add_row(str(json_response["chain_id"]), json_response["name"])

            console.print(table)

    except Exception:
        return


@chains_app.command("list")
def list_chains():
    response = make_request_with_api_key("GET", V1Routes.CHAINS)

    json_response = response.json()

    table = Table(show_header=True, header_style="green")
    table.add_column("Chain ID")
    table.add_column("Name")

    for item in json_response["items"]:
        print()
        table.add_row(str(item["chain_id"]), item["name"])

    console.print(table)


@chains_app.command("delete")
def delete_chain(
    chain_id: Optional[int] = Argument(None, help="The ID of the chain to delete.")
):
    if chain_id is None:
        chain_id = prompt("Enter the ID of the chain to delete", type=int)

    try:
        response = make_request_with_api_key("DELETE", f"{V1Routes.CHAINS}/{chain_id}")

        if response.status_code == 204:
            console.print(f"Successfully deleted chain {chain_id}")

    except Exception:
        return
