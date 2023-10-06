from typing_extensions import Annotated
from typer import Typer, Option, Argument
from rich.console import Console
from rich.table import Table

from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file

from cli.types.offerings import OfferingCreate, OfferingUpdate

console = Console()
offerings_app = Typer()


@offerings_app.command("detail")
def offerings(id: Annotated[str, Argument()]):
    response = make_request_with_api_key("GET", f"{V1Routes.OFFERINGS}/{id}")

    if response.status_code == 404:
        console.print("Offering not found")

    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Provider")
    table.add_column("Chain")
    table.add_column("Entrypoints")

    offering = response.json()

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
    offerings = response.json()

    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Provider")
    table.add_column("Chain")
    table.add_column("Entrypoints")

    for item in offerings["items"]:
        offering_id = item["id"]
        provider_name = item["provider"]["name"]
        chain_name = item["chain"]["name"]
        entrypoint_count = len(item["entrypoints"])
        table.add_row(offering_id, provider_name, chain_name, str(entrypoint_count))

    console.print(table)


@offerings_app.command("create")
def offerings_create(config_file: str = Option()):
    offering_create = parse_config_file(config_file, OfferingCreate)
    response = make_request_with_api_key(
        "POST", V1Routes.OFFERINGS, offering_create.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 201:
        console.print(f"Successfully created offering {json_response['id']}")
    else:
        console.print(f"Error creating offering: {json_response['detail']}")


@offerings_app.command("update")
def offerings_update(
    offering_id: str = Argument(..., help="The UUID of the offering to update."),
    config_file: str = Option(
        ..., help="The path to a JSON file with the update data."
    ),
):
    offering_update = parse_config_file(config_file, OfferingUpdate)
    response = make_request_with_api_key(
        "PATCH",
        f"{V1Routes.OFFERINGS}/{offering_id}",
        offering_update.model_dump_json(),
    )

    json_response = response.json()

    if response.status_code == 200:
        console.print(f"Successfully updated offering {json_response['id']}")
    else:
        console.print(f"Error updating offering: {json_response['detail']}")


@offerings_app.command("delete")
def offerings_delete(
    offering_id: str = Argument(..., help="The UUID of the offering to delete.")
):
    response = make_request_with_api_key(
        "DELETE", f"{V1Routes.OFFERINGS}/{offering_id}"
    )

    if response.status_code == 204:
        console.print(f"Successfully deleted offering {offering_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting offering: {json_response['detail']}")
