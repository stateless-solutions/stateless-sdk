import ujson
from typer import Typer, Option, Argument, prompt
from typing import Optional
from rich.console import Console
from rich.table import Table

from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file

from cli.models.entrypoints import EntrypointCreate, EntrypointUpdate

console = Console()
entrypoints_app = Typer()


@entrypoints_app.command("list")
def entrypoint_list():
    response = make_request_with_api_key("GET", V1Routes.LIST_ENTRYPOINTS)
    entrypoints = response.json()

    # TODO: fix joined loads so we display provider/chain names instead of IDs
    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Region")
    table.add_column("Provider ID")
    table.add_column("Chain ID")

    for item in entrypoints["items"]:
        entrypoint_id = item["id"]
        region_name = item["region"]["name"]
        provider_id = item["offering"]["provider_id"]
        chain_id = item["offering"]["chain_id"]
        table.add_row(entrypoint_id, region_name, provider_id, str(chain_id))

    console.print(table)


@entrypoints_app.command("create")
def entrypoint_create(config_file: Optional[str] = Option(None)):
    if config_file:
        entrypoint_create = parse_config_file(config_file, EntrypointCreate)
    else:
        # Interactive Prompts for Entrypoint Creation
        url = prompt("Enter the URL of the entrypoint")
        offering_id = prompt("Enter the ID of the offering for the entrypoint", type=str)
        region_id = prompt("Enter the ID of the region for the entrypoint", type=str)

        entrypoint_create = EntrypointCreate(url=url, offering_id=offering_id, region_id=region_id)
        
    response = make_request_with_api_key(
        "POST", V1Routes.ENTRYPOINTS, entrypoint_create.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 201:
        console.print(
            f"Successfully created entrypoint {json_response['id']} with the following URL: {json_response['url']}"
        )
    else:
        console.print(f"Error creating entrypoint: {json_response['detail']}")


@entrypoints_app.command("get")
def entrypoint_get(entrypoint_id: Optional[str] = Argument(None, help="The UUID of the entrypoint to get.")):
    if not entrypoint_id:
        entrypoint_id = prompt("Enter the UUID of the entrypoint to get")
        
    response = make_request_with_api_key(
        "GET", f"{V1Routes.ENTRYPOINTS}/{entrypoint_id}"
    )

    json_response = response.json()

    if response.status_code == 200:
        console.print(ujson.dumps(json_response, indent=2))
    else:
        console.print(f"Error getting entrypoint: {json_response['detail']}")


@entrypoints_app.command("update")
def entrypoint_update(
    entrypoint_id: Optional[str] = Argument(None, help="The UUID of the entrypoint to update."),
    config_file: Optional[str] = Option(None, help="The path to a JSON file with the update data.")
):
    if not entrypoint_id:
        entrypoint_id = prompt("Enter the UUID of the entrypoint to update")

    if config_file:
        entrypoint_update = parse_config_file(config_file, EntrypointUpdate)
    else:
        url = prompt("Enter the updated URL of the entrypoint", default=None)

        entrypoint_update = EntrypointUpdate(url=url)

    response = make_request_with_api_key(
        "PATCH",
        f"{V1Routes.ENTRYPOINTS}/{entrypoint_id}",
        entrypoint_update.model_dump_json(),
    )

    json_response = response.json()

    if response.status_code == 200:
        console.print(f"Successfully updated entrypoint {json_response['id']}")
    else:
        console.print(f"Error updating entrypoint: {json_response['detail']}")


@entrypoints_app.command("delete")
def entrypoint_delete(entrypoint_id: Optional[str] = Argument(None, help="The UUID of the entrypoint to delete.")):
    if not entrypoint_id:
        entrypoint_id = prompt("Enter the UUID of the entrypoint to delete")
        
    response = make_request_with_api_key(
        "DELETE", f"{V1Routes.ENTRYPOINTS}/{entrypoint_id}"
    )

    if response.status_code == 204:
        console.print(f"Successfully deleted entrypoint {entrypoint_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting entrypoint: {json_response['detail']}")
