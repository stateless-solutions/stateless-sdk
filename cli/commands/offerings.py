import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file, handle_api_response
from cli.models.offerings import OfferingCreate, OfferingUpdate

console = Console()
offerings_app = typer.Typer()


def prompt_for_offering_create() -> OfferingCreate:
    try:
        chain_id = typer.prompt("Chain ID", type=int)
        provider_id = typer.prompt("Provider ID")
        return OfferingCreate(chain_id=chain_id, provider_id=provider_id)
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


def prompt_for_offering_update() -> OfferingUpdate:
    try:
        chain_id = typer.prompt("Updated Chain ID", type=int, default=None)
        provider_id = typer.prompt("Updated Provider ID", default=None)
        return OfferingUpdate(chain_id=chain_id, provider_id=provider_id)
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


@offerings_app.command("detail")
def offerings_detail(id: typer.Argument(...)):
    response = make_request_with_api_key("GET", f"{V1Routes.OFFERINGS}/{id}")
    if response.status_code == 404:
        console.print("Offering not found")
        raise typer.Exit(code=1)

    offering = response.json()
    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Provider")
    table.add_column("Chain")
    table.add_column("Entrypoints")

    offering_id = offering["id"]
    provider_name = offering["provider"]["name"]
    chain_name = offering["chain"]["name"]
    entrypoints_urls = [entrypoint["url"] for entrypoint in offering["entrypoints"]]
    entrypoints = "\n".join(entrypoints_urls)
    table.add_row(offering_id, provider_name, chain_name, entrypoints)

    console.print(table)


@offerings_app.command("list")
def offerings_list():
    response = make_request_with_api_key("GET", V1Routes.LIST_OFFERINGS)
    offerings = response.json()["items"]

    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Provider")
    table.add_column("Chain")
    table.add_column("Entrypoints")

    for item in offerings:
        offering_id = item["id"]
        provider_name = item["provider"]["name"]
        chain_name = item["chain"]["name"]
        entrypoint_count = len(item["entrypoints"])
        table.add_row(offering_id, provider_name, chain_name, str(entrypoint_count))

    console.print(table)


@offerings_app.command("create")
def offerings_create(
    config_file: str = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the offering creation data.",
    )
):
    try:
        if config_file:
            offering_create = parse_config_file(config_file, OfferingCreate)
        else:
            offering_create = prompt_for_offering_create()
        response = make_request_with_api_key(
            "POST", V1Routes.OFFERINGS, offering_create.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@offerings_app.command("update")
def offerings_update(
    offering_id: str = typer.Argument(..., help="The UUID of the offering to update."),
    config_file: str = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the update data.",
    ),
):
    try:
        offering_id = offering_id or typer.prompt("Offering ID")
        if config_file:
            offering_update = parse_config_file(config_file, OfferingUpdate)
        else:
            offering_update = prompt_for_offering_update()
        response = make_request_with_api_key(
            "PATCH", f"{V1Routes.OFFERINGS}/{offering_id}", offering_update.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@offerings_app.command("delete")
def offerings_delete(
    offering_id: str = typer.Argument(..., help="The UUID of the offering to delete.")
):
    try:
        response = make_request_with_api_key(
            "DELETE", f"{V1Routes.OFFERINGS}/{offering_id}"
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


if __name__ == "__main__":
    offerings_app()
