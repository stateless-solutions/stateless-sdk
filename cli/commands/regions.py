import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file, handle_api_response
from cli.models.regions import RegionCreate, RegionUpdate

console = Console()
regions_app = typer.Typer()


def prompt_for_region_create() -> RegionCreate:
    try:
        name = typer.prompt("Name")
        return RegionCreate(name=name)
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


def prompt_for_region_update() -> RegionUpdate:
    try:
        name = typer.prompt("Updated Name")
        return RegionUpdate(name=name)
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


@regions_app.command("create")
def create_region(
    config_file: str = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the region creation data.",
    )
):
    try:
        if config_file:
            region_create = parse_config_file(config_file, RegionCreate)
        else:
            region_create = prompt_for_region_create()
        response = make_request_with_api_key(
            "POST", V1Routes.REGIONS, region_create.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@regions_app.command("get")
def get_region(
    region_id: str = typer.Argument(..., help="The ID of the region to get.")
):
    try:
        response = make_request_with_api_key("GET", f"{V1Routes.REGIONS}/{region_id}")
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@regions_app.command("list")
def list_regions():
    try:
        response = make_request_with_api_key("GET", V1Routes.LIST_REGIONS)
        regions = response.json()["items"]
        table = Table(show_header=True, header_style="green")
        table.add_column("ID")
        table.add_column("Name")

        for item in regions:
            table.add_row(item["id"], item["name"])
        console.print(table)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@regions_app.command("update")
def update_region(
    region_id: str = typer.Argument(..., help="The ID of the region to update."),
    config_file: str = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the region update data.",
    ),
):
    try:
        if config_file:
            region_update = parse_config_file(config_file, RegionUpdate)
        else:
            region_update = prompt_for_region_update()
        response = make_request_with_api_key(
            "PATCH", f"{V1Routes.REGIONS}/{region_id}", region_update.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@regions_app.command("delete")
def delete_region(
    region_id: str = typer.Argument(..., help="The ID of the region to delete.")
):
    try:
        response = make_request_with_api_key(
            "DELETE", f"{V1Routes.REGIONS}/{region_id}"
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


if __name__ == "__main__":
    regions_app()
