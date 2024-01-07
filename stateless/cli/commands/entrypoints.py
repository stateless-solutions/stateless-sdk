from typing import Optional

import inquirer
import ujson
from rich.console import Console
from rich.table import Table
from typer import Argument, Option, Typer, Exit

from ..models.entrypoints import EntrypointCreate, EntrypointUpdate
from ..routes import V1Routes
from ..utils import make_request_with_api_key, parse_config_file, secho

console = Console()
entrypoints_app = Typer()

class EntrypointsManager:
    @staticmethod
    def _get_offerings():
        response = make_request_with_api_key("GET", V1Routes.LIST_OFFERINGS)
        offerings = response.json().get("items")
        if not offerings:
            raise Exit(secho(
                    f"You dont have any offerings, please add an offering by running `stateless-cli offerings --help`",
                    fg="red"))
        return offerings

    @staticmethod
    def _get_regions():
        response = make_request_with_api_key("GET", V1Routes.REGIONS)
        return response.json()["items"]

    @staticmethod
    def _select_entrypoint(prompt_message):
        entrypoints = [
            (item["url"], item["id"])
            for item in EntrypointsManager._get_offerings()
        ]
        questions = [
            inquirer.List(
                "entrypoint",
                message=prompt_message,
                choices=entrypoints,
                carousel=True,
            ),
        ]
        answers = inquirer.prompt(questions)
        return answers["entrypoint"]

    @staticmethod
    def _print_table(items, columns):
        table = Table(show_header=True, header_style="green", padding=(0, 1, 0, 1))
        for col in columns:
            table.add_column(col)

        for item in items:
            table.add_row(*item, end_section=True)

        console.print(table)

@entrypoints_app.command("create")
def entrypoint_create(config_file: Optional[str] = Option(None, "--config-file", "-c")):
    if config_file:
        entrypoint_create = parse_config_file(config_file, EntrypointCreate)
    else:
        offerings = [(item["chain"]["name"], item["id"]) for item in EntrypointsManager._get_offerings()]
        regions = [(item["name"], item["id"]) for item in EntrypointsManager._get_regions()]
        questions = [
            inquirer.List("offering", message="Which offering would you like to create an entrypoint for?", choices=offerings, carousel=True),
            inquirer.List("region", message="Which region would you like to create an entrypoint in?", choices=regions, carousel=True),
            inquirer.Text("url", message="What is the URL of the entrypoint?", validate=lambda _, x: x.startswith("https://") or x.startswith("http://")),
        ]
        answers = inquirer.prompt(questions)
        entrypoint_create = EntrypointCreate(url=answers["url"], offering_id=answers["offering"], region_id=answers["region"])

    response = make_request_with_api_key("POST", V1Routes.ENTRYPOINTS, entrypoint_create.model_dump_json())
    json_response = response.json()

    if response.status_code == 201:
        console.print(f"Successfully created entrypoint with the following URL: {json_response['url']}")
    else:
        console.print(f"Error creating entrypoint: {json_response['detail']}")

@entrypoints_app.command("get")
def entrypoint_get(entrypoint_id: Optional[str] = Argument(None, help="The UUID of the entrypoint to get.")):
    entrypoint_id = entrypoint_id or EntrypointsManager._select_entrypoint("What's the ID of entrypoint you want to obtain?")
    response = make_request_with_api_key("GET", f"{V1Routes.ENTRYPOINTS}/{entrypoint_id}")
    json_response = response.json()

    if response.status_code == 200:
        console.print(ujson.dumps(json_response, indent=2))
    else:
        console.print(f"Error getting entrypoint: {json_response['detail']}")

@entrypoints_app.command("update")
def entrypoint_update(
    entrypoint_id: Optional[str] = Argument(None, help="The UUID of the entrypoint to update."),
    config_file: Optional[str] = Option(None, "--config-file", "-c", help="The path to a JSON file with the update data."),
):
    entrypoint_id = entrypoint_id or EntrypointsManager._select_entrypoint("What's the ID of the entrypoint you want to update?")
    if config_file:
        entrypoint_update = parse_config_file(config_file, EntrypointUpdate)
    else:
        questions = [inquirer.Text("url", message="What's the new URL of the entrypoint?")]
        answers = inquirer.prompt(questions)
        entrypoint_update = EntrypointUpdate(url=answers["url"])

    response = make_request_with_api_key("PATCH", f"{V1Routes.ENTRYPOINTS}/{entrypoint_id}", entrypoint_update.model_dump_json())
    json_response = response.json()

    if response.status_code == 200:
        console.print(f"Successfully updated entrypoint {json_response['id']}")
    else:
        console.print(f"Error updating entrypoint: {json_response['detail']}")

@entrypoints_app.command("delete")
def entrypoint_delete(entrypoint_id: Optional[str] = Argument(None, help="The UUID of the entrypoint to delete.")):
    entrypoint_id = entrypoint_id or EntrypointsManager._select_entrypoint("What's the ID of the entrypoint you want to delete?")
    response = make_request_with_api_key("DELETE", f"{V1Routes.ENTRYPOINTS}/{entrypoint_id}")

    if response.status_code == 204:
        console.print(f"Successfully deleted entrypoint {entrypoint_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting entrypoint: {json_response['detail']}")

@entrypoints_app.command("list")
def entrypoint_list(offering_id: Optional[str] = Argument(None, help="The UUID of the offering to list entrypoints for.")):
    offerings = [(item["chain"]["name"], item["id"]) for item in EntrypointsManager._get_offerings()]
    questions = [
            inquirer.List("offering", message="Which offering would you like to list entrypoints for?", choices=offerings, carousel=True)
        ]
    answers = inquirer.prompt(questions)
    offering_id = offering_id or answers["offering"]
    response = make_request_with_api_key("GET", f"{V1Routes.OFFERINGS}/{offering_id}")
    json_response = response.json()

    if response.status_code == 200:
        items = [
            (str(entrypoint["id"]), entrypoint["url"], entrypoint["region"]["name"])
            for entrypoint in json_response["entrypoints"]
        ]
        EntrypointsManager._print_table(items, ["Entrypoint ID", "URL", "Region"])
    else:
        console.print(f"Error listing entrypoints: {json_response['detail']}")

