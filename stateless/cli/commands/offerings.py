from typing import Optional

import inquirer
from rich.console import Console
from typer import Argument, Option, Typer

from ..models.offerings import OfferingCreate, OfferingUpdate
from ..routes import V1Routes
from ..utils import (
    BaseManager,
    make_request_with_api_key,
    parse_config_file,
    provider_guard,
)
from .entrypoints import entrypoint_create

console = Console()
offerings_app = Typer()


class OfferingsManager(BaseManager):
    @staticmethod
    def _get_offerings(chain_id: Optional[int] = None, offset=0, limit=10):
        params = {}
        if chain_id is not None:
            params["chain_id"] = chain_id
        return OfferingsManager.make_paginated_request(
            V1Routes.LIST_OFFERINGS, offset, limit, params=params
        )

    @staticmethod
    def _select_offering(prompt_message, chain_id=None):
        offerings = [
            (f"{item['chain']['name']} - {item['provider']['name']}", item["id"])
            for item in OfferingsManager._get_offerings(chain_id)["items"]
        ]
        questions = [
            inquirer.List(
                "offering",
                message=prompt_message,
                choices=offerings,
                carousel=True,
            ),
        ]
        answers = inquirer.prompt(questions)
        return answers["offering"]

    @staticmethod
    def _select_offerings(prompt_message, chain_id=None, selected_offerings=None):
        offerings = OfferingsManager._get_offerings(chain_id)["items"]
        choices = [
            (
                "{}".format(offering["provider"]["name"]),
                offering["id"],
            )
            for offering in offerings
        ]
        questions = [
            inquirer.Checkbox(
                "offerings",
                message=prompt_message,
                choices=choices,
                default=selected_offerings,
                carousel=True,
            )
        ]
        answers = inquirer.prompt(questions)

        return answers["offerings"]


@offerings_app.command("view")
def offerings_detail(id: Optional[str] = Argument(None)):
    offering_id = id or OfferingsManager._select_offering(
        "Which offering would you like to view?"
    )
    response = make_request_with_api_key("GET", f"{V1Routes.OFFERINGS}/{offering_id}")

    if response.status_code == 404:
        console.print("Offering not found")
        return

    if response.status_code == 200:
        offering = response.json()
        entrypoints_urls = [
            entrypoint["url"] if "url" in entrypoint else "Redacted :)"
            for entrypoint in offering["entrypoints"]
        ]
        entrypoints = "\n".join(entrypoints_urls)
        OfferingsManager._print_table(
            [
                (
                    offering["id"],
                    offering["provider"]["name"],
                    entrypoints,
                )
            ],
            ["ID", "Provider", "Entrypoints"],
        )


@offerings_app.command("list")
def offerings_list(
    limit: int = Option(10, help="Number of offerings per page."),
    chain_id: Optional[int] = None,
):
    offset = 0
    while True:
        response = OfferingsManager._get_offerings(
            chain_id=chain_id, offset=offset, limit=limit
        )
        offerings = response["items"]
        total = response.get("total", 0)

        items = [
            (
                offering["id"],
                offering["provider"]["name"],
                offering["chain"]["name"],
                str(len(offering["entrypoints"])),
                ", ".join(
                    {
                        entrypoint["region"]["name"]
                        for entrypoint in offering["entrypoints"]
                        if "region" in entrypoint
                    }
                ),
            )
            for offering in offerings
        ]
        OfferingsManager._print_table(
            items, ["ID", "Provider", "Chain", "Entrypoints", "Regions"]
        )

        if not offerings or len(offerings) < limit or offset + limit >= total:
            console.print("End of offerings list.")
            break

        navigate = inquirer.list_input(
            "Navigate pages", choices=["Next", "Previous", "Exit"], carousel=True
        )

        if navigate == "Next":
            offset += limit
        elif navigate == "Previous" and offset - limit >= 0:
            offset -= limit
        else:
            break


@offerings_app.command("create")
def offerings_create(
    config_file: Optional[str] = Option(None, "--config-file", "-c"),
):
    provider_guard()
    if config_file:
        offering_create = parse_config_file(config_file, OfferingCreate)
    else:
        response = make_request_with_api_key("GET", V1Routes.CHAINS)
        chains = [
            (str(item["name"]), str(item["chain_id"]))
            for item in response.json()["items"]
        ]
        questions = [
            inquirer.List(
                "chain",
                message="What is the target blockchain platform for this offering?",
                choices=chains,
                carousel=True,
            )
        ]
        answers = inquirer.prompt(questions)
        offering_create = OfferingCreate(chain_id=answers["chain"])

    response = make_request_with_api_key(
        "POST", V1Routes.OFFERINGS, offering_create.model_dump_json()
    )
    json_response = response.json()

    if response.status_code == 201:
        console.print(
            f"Your offering has been created successfully with ID: {json_response['id']}"
        )

        add_entrypoints = inquirer.confirm(
            message="Would you like to add entrypoints to this offering now?",
            default=False,
        )

        if add_entrypoints:
            entrypoint_create(None)
        else:
            console.print(
                "You can now add entrypoints to this offering with `stateless-cli entrypoints create`"
            )

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
    provider_guard()
    offering_id = offering_id or OfferingsManager._select_offering(
        "Which offering would you like to update?"
    )

    if config_file:
        offering_update = parse_config_file(config_file, OfferingUpdate)
    else:
        questions = [
            inquirer.Text(
                "chain_id",
                message="What's the new chain ID you want to set for the offering?",
            )
        ]
        answers = inquirer.prompt(questions)
        offering_update = OfferingUpdate(chain_id=answers["chain_id"])

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
    provider_guard()
    offering_id = offering_id or OfferingsManager._select_offering(
        "Which offering would you like to delete?"
    )
    response = make_request_with_api_key(
        "DELETE", f"{V1Routes.OFFERINGS}/{offering_id}"
    )

    if response.status_code == 204:
        console.print(f"Successfully deleted offering {offering_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting offering: {json_response['detail']}")
