import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file, handle_api_response
from cli.models.chains import ChainCreate, ChainUpdate

console = Console()
chains_app = typer.Typer()


def prompt_for_chain_create() -> ChainCreate:
    try:
        chain_id = typer.prompt("Chain ID", type=int)
        name = typer.prompt("Chain Name")
        return ChainCreate(chain_id=chain_id, name=name)
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


def prompt_for_chain_update() -> ChainUpdate:
    try:
        name = typer.prompt("New Chain Name", default=None)
        return ChainUpdate(name=name)
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


@chains_app.command("create")
def create_chain(
    config_file: str = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the chain creation data.",
    )
):
    try:
        if config_file:
            chain_create = parse_config_file(config_file, ChainCreate)
        else:
            chain_create = prompt_for_chain_create()
        response = make_request_with_api_key(
            "POST", V1Routes.CHAINS, chain_create.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@chains_app.command("update")
def update_chain(
    chain_id: int = typer.Argument(None, help="The ID of the chain to update."),
    config_file: str = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the update data.",
    ),
):
    try:
        chain_id = chain_id or typer.prompt("Chain ID", type=int)
        if config_file:
            chain_update = parse_config_file(config_file, ChainUpdate)
        else:
            chain_update = prompt_for_chain_update()
        response = make_request_with_api_key(
            "PATCH", f"{V1Routes.CHAINS}/{chain_id}", chain_update.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@chains_app.command("get")
def get_chain(chain_id: int = typer.Argument(None, help="The ID of the chain to get.")):
    try:
        chain_id = chain_id or typer.prompt("Chain ID", type=int)
        response = make_request_with_api_key("GET", f"{V1Routes.CHAINS}/{chain_id}")
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@chains_app.command("list")
def list_chains():
    try:
        response = make_request_with_api_key("GET", V1Routes.LIST_CHAINS)
        if response.status_code == 200:
            json_response = response.json()
            table = Table(show_header=True, header_style="bold green")
            table.add_column("ID", style="dim")
            table.add_column("Name")

            for item in json_response["items"]:
                table.add_row(
                    str(item["chain_id"]), item["name"]
                )  # Ensure ID is a string for rich to display

            console.print(table)
        else:
            console.print(f"Error retrieving chains: {response.text}", style="bold red")
            raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@chains_app.command("delete")
def delete_chain(
    chain_id: int = typer.Argument(None, help="The ID of the chain to delete.")
):
    try:
        chain_id = chain_id or typer.prompt("Chain ID", type=int)
        response = make_request_with_api_key("DELETE", f"{V1Routes.CHAINS}/{chain_id}")
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


if __name__ == "__main__":
    chains_app()
