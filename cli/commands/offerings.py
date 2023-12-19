from typing import Optional

import inquirer
from rich.console import Console
from rich.table import Table
from typer import Argument, Option, Typer

from cli.models.offerings import OfferingCreate, OfferingUpdate
from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file

console = Console()
offerings_app = Typer()


@offerings_app.command("detail")
def offerings_detail(id: Optional[str] = Argument(None)):
    if not id:
        response = make_request_with_api_key("GET", V1Routes.LIST_OFFERINGS)
        json_response = response.json()

        offerings = []
        for item in json_response["items"]:
            offering = (
                f"{item['chain']['name']} - {item['provider']['name']}",
                item["id"],
            )
            offerings.append(offering)
        questions = [
            inquirer.List(
                "offering",
                message="Which offering would you like to list entrypoints for?",
                choices=offerings,
                carousel=True,
            ),
        ]
        answers = inquirer.prompt(questions)
        offering_id = answers["offering"]

    response = make_request_with_api_key("GET", f"{V1Routes.OFFERINGS}/{offering_id}")

    if response.status_code == 404:
        console.print("Offering not found")

    if response.status_code == 200:
        table = Table(show_header=True, header_style="green")
        table.add_column("ID")
        table.add_column("Provider")
        table.add_column("Chain")
        table.add_column("Entrypoints")

        offering = response.json()

        offering_id = offering["id"]
        provider_name = offering["provider"]["name"]
        chain_name = offering["chain"]["name"]
        entrypoints_urls = [
            entrypoint["url"] if "url" in entrypoint else "Redacted :)"
            for entrypoint in offering["entrypoints"]
        ]
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
def offerings_create(
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
    ),
):
    if config_file:
        offering_create = parse_config_file(config_file, OfferingCreate)
    else:
        response = make_request_with_api_key("GET", V1Routes.CHAINS)

        chains = []
        json_response = response.json()
        for item in json_response["items"]:
            chain = (str(item["name"]), str(item["chain_id"]))
            chains.append(chain)

        questions = [
            inquirer.List(
                "chain",
                message="What is the target blockchain platform for this offering?",
                choices=chains,
                carousel=True,
            ),
        ]
        answers = inquirer.prompt(questions)
        chain_id = answers["chain"]
        offering_create = OfferingCreate(chain_id=chain_id)

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
    offering_id: Optional[str] = Argument(
        None, help="The UUID of the offering to update."
    ),
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the update data.",
    ),
):
    if not offering_id:
        response = make_request_with_api_key("GET", V1Routes.LIST_OFFERINGS)
        json_response = response.json()

        offerings = []
        for item in json_response["items"]:
            offering = (
                f"{item['chain']['name']} - {item['provider']['name']}",
                item["id"],
            )
            offerings.append(offering)
        questions = [
            inquirer.List(
                "offering",
                message="Which offering would you like to update?",
                choices=offerings,
                carousel=True,
            ),
        ]
        answers = inquirer.prompt(questions)
        offering_id = answers["offering"]

    if config_file:
        offering_update = parse_config_file(config_file, OfferingUpdate)
    else:
        questions = [
            inquirer.Text(
                "chain_id",
                message="What's the new chain ID you want to set for the offering?",
            ),
        ]
        answers = inquirer.prompt(questions)
        chain_id = answers["chain_id"]

        offering_update = OfferingUpdate(chain_id=chain_id)

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
    offering_id: Optional[str] = Argument(
        None, help="The UUID of the offering to delete."
    ),
):
    if not offering_id:
        response = make_request_with_api_key("GET", V1Routes.LIST_OFFERINGS)
        json_response = response.json()

        offerings = []
        for item in json_response["items"]:
            offering = (
                f"{item['chain']['name']} - {item['provider']['name']}",
                item["id"],
            )
            offerings.append(offering)
        questions = [
            inquirer.List(
                "offering",
                message="Which offering would you like to delete?",
                choices=offerings,
                carousel=True,
            ),
        ]
        answers = inquirer.prompt(questions)
        offering_id = answers["offering"]

    response = make_request_with_api_key(
        "DELETE", f"{V1Routes.OFFERINGS}/{offering_id}"
    )

    if response.status_code == 204:
        console.print(f"Successfully deleted offering {offering_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting offering: {json_response['detail']}")
