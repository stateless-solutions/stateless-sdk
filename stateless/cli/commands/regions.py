from typing import Optional

from rich.console import Console
from rich.table import Table
from typer import Argument, Option, Typer, prompt

from ..models.regions import RegionCreate, RegionUpdate
from ..routes import V1Routes
from ..utils import make_request_with_api_key, parse_config_file

console = Console()
regions_app = Typer()


@regions_app.command("create")
def create_region(
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the region creation data.",
    ),
):
    if config_file:
        region_create = parse_config_file(config_file, RegionCreate)
    else:
        name = prompt("Enter the name of the region")
        region_create = RegionCreate(name=name)

    response = make_request_with_api_key(
        "POST", V1Routes.REGIONS, region_create.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 201:
        console.print(f"Successfully created region {json_response['id']}")
    else:
        console.print(f"Error creating region: {json_response['detail']}")


@regions_app.command("view")
def get_region(
    region_id: Optional[str] = Argument(None, help="The ID of the region to view.")
):
    if not region_id:
        region_id = prompt("Enter the ID of the region to view")

    response = make_request_with_api_key("GET", f"{V1Routes.REGIONS}/{region_id}")

    json_response = response.json()

    if response.status_code == 200:
        console.print(json_response)  # Display the region details
    else:
        console.print(f"Error getting region: {json_response['detail']}")


@regions_app.command("list")
def list_regions():
    response = make_request_with_api_key("GET", V1Routes.LIST_REGIONS)

    json_response = response.json()

    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Name")
    # Add more columns as needed

    for item in json_response["items"]:
        table.add_row(item["id"], item["name"])  # Add more columns as needed

    console.print(table)


@regions_app.command("update")
def update_region(
    region_id: str = Argument(..., help="The ID of the region to update."),
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the region update data.",
    ),
):
    if config_file:
        region_update = parse_config_file(config_file, RegionUpdate)
    else:
        name = prompt("Enter the updated name of the region", default=None)
        region_update = RegionUpdate(name=name)

    response = make_request_with_api_key(
        "PATCH", f"{V1Routes.REGIONS}/{region_id}", region_update.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 200:
        console.print(f"Successfully updated region {json_response['id']}")
    else:
        console.print(f"Error updating region: {json_response['detail']}")


@regions_app.command("delete")
def delete_region(
    region_id: Optional[str] = Argument(None, help="The ID of the region to delete.")
):
    if not region_id:
        region_id = prompt("Enter the ID of the region to delete")

    response = make_request_with_api_key("DELETE", f"{V1Routes.REGIONS}/{region_id}")

    if response.status_code == 204:
        console.print(f"Successfully deleted region {region_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting region: {json_response['detail']}")
