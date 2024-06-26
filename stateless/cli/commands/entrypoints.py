from typing import Optional

import inquirer
from rich.console import Console
from typer import Argument, Exit, Option, Typer, prompt

from ..models.entrypoints import (
    EntrypointCreate,
    EntrypointUpdate,
    InternalProviderEntrypointCreate,
    InternalProviderEntrypointUpdate,
)
from ..routes import V1Routes
from ..utils import (
    BaseManager,
    admin_guard,
    make_request_with_api_key,
    parse_config_file,
    provider_guard,
    secho,
)

console = Console()
entrypoints_app = Typer()


class EntrypointsManager(BaseManager):
    @staticmethod
    def _get_offerings(chain_id: Optional[int] = None, offset=0, limit=10):
        params = {"chain_id": chain_id} if chain_id else {}
        offerings = EntrypointsManager.make_paginated_request(
            V1Routes.LIST_OFFERINGS, offset, limit, params=params
        )
        if not offerings:
            raise Exit(
                secho(
                    "You dont have any offerings, please add an offering by running `stateless-cli offerings --help`",
                    fg="red",
                )
            )
        return offerings

    @staticmethod
    def _get_internal_provider_entrypoints(offset=0, limit=10):
        internal_provider_entrypoints = EntrypointsManager.make_paginated_request(
            V1Routes.INTERNAL_PROVIDER_ENTRYPOINTS, offset, limit
        )
        if not internal_provider_entrypoints:
            raise Exit(
                secho(
                    "No internal provider entrypoints found.",
                    fg="red",
                )
            )
        return internal_provider_entrypoints

    @staticmethod
    def _get_regions():
        response = make_request_with_api_key("GET", V1Routes.REGIONS)
        return response.json()["items"]

    @staticmethod
    def _select_entrypoint(prompt_message):
        offset = 0
        limit = 10
        selected_entrypoint = None
        while selected_entrypoint is None:
            response = EntrypointsManager._get_offerings(offset=offset, limit=limit)
            offerings = response["items"]
            total = response["total"]

            if not offerings and offset == 0:  # No offerings available at all
                console.print("No entrypoints available.")
                return None

            entrypoints = []
            for offering in offerings:
                chain_name = offering["chain"]["name"]
                for entrypoint in offering["entrypoints"]:
                    region = entrypoint["region"]["name"]
                    item = "{} - {}: {}".format(chain_name, region, entrypoint["url"])
                    entrypoints.append((item, entrypoint["id"]))

            # entrypoints = [(item["url"], item["id"]) for item in offerings]
            navigation_message = ""
            if offset > 0:
                entrypoints.insert(0, ("Previous Page", "prev"))
                navigation_message += "[bold yellow]Previous Page: Go back to the previous page.[/bold yellow]"
            if total > offset + limit:
                entrypoints.append(("Next Page", "next"))
                navigation_message += "[bold yellow]Next Page: Move to the next page of entrypoints.[/bold yellow]"

            if navigation_message:
                console.print(navigation_message)

            questions = [
                inquirer.List(
                    "entrypoint",
                    message=prompt_message,
                    choices=entrypoints,
                    carousel=True,
                ),
            ]
            answers = inquirer.prompt(questions)
            choice = answers["entrypoint"]

            if choice == "next":
                offset += limit
            elif choice == "prev":
                offset = max(0, offset - limit)
            else:
                selected_entrypoint = choice

        return selected_entrypoint

    @staticmethod
    def _select_internal_entrypoint(prompt_message):
        offset = 0
        limit = 10
        selected_internal_entrypoint = None
        while selected_internal_entrypoint is None:
            response = EntrypointsManager._get_internal_provider_entrypoints(
                offset=offset, limit=limit
            )
            internal_entrypoints = response["items"]
            total = response["total"]

            if (
                not internal_entrypoints and offset == 0
            ):  # No internal entrypoints available at all
                console.print("No internal entrypoints available.")
                return None

            entrypoints = []
            for internal_entrypoint in internal_entrypoints:
                item = "{} - {} - {} - {}".format(
                    internal_entrypoint["id"],
                    str(internal_entrypoint["chain_id"]),
                    internal_entrypoint["url"],
                    internal_entrypoint["identity"],
                )
                entrypoints.append((item, internal_entrypoint["id"]))

            navigation_message = ""
            if offset > 0:
                entrypoints.insert(0, ("Previous Page", "prev"))
                navigation_message += "[bold yellow]Previous Page: Go back to the previous page.[/bold yellow]"
            if total > offset + limit:
                entrypoints.append(("Next Page", "next"))
                navigation_message += "[bold yellow]Next Page: Move to the next page of entrypoints.[/bold yellow]"

            if navigation_message:
                console.print(navigation_message)

            questions = [
                inquirer.List(
                    "entrypoint",
                    message=prompt_message,
                    choices=entrypoints,
                    carousel=True,
                ),
            ]
            answers = inquirer.prompt(questions)
            choice = answers["entrypoint"]

            if choice == "next":
                offset += limit
            elif choice == "prev":
                offset = max(0, offset - limit)
            else:
                selected_internal_entrypoint = choice

        return selected_internal_entrypoint


@entrypoints_app.command("create")
def entrypoint_create(config_file: Optional[str] = Option(None, "--config-file", "-c")):
    provider_guard()
    while True:
        if config_file:
            entrypoint_create = parse_config_file(config_file, EntrypointCreate)
        else:
            offerings = [
                (item["chain"]["name"], item["id"])
                for item in EntrypointsManager._get_offerings()["items"]
            ]
            regions = [
                (item["name"], item["id"]) for item in EntrypointsManager._get_regions()
            ]
            questions = [
                inquirer.List(
                    "offering",
                    message="Which offering would you like to create an entrypoint for?",
                    choices=offerings,
                    carousel=True,
                ),
                inquirer.List(
                    "region",
                    message="Which region would you like to create an entrypoint in?",
                    choices=regions,
                    carousel=True,
                ),
                inquirer.Text(
                    "url",
                    message="What is the URL of the entrypoint?",
                    validate=lambda _, x: x.startswith("https://")
                    or x.startswith("http://"),
                ),
            ]
            answers = inquirer.prompt(questions)
            entrypoint_create = EntrypointCreate(
                url=answers["url"],
                offering_id=answers["offering"],
                region_id=answers["region"],
            )

        response = make_request_with_api_key(
            "POST", V1Routes.ENTRYPOINTS, entrypoint_create.model_dump_json()
        )
        json_response = response.json()

        if response.status_code == 201:
            console.print(
                f"Successfully created entrypoint with the following URL: {json_response['url']}"
            )
            create_another = inquirer.confirm(
                "Would you like to create another entrypoint?"
            )
            if not create_another:
                break
        else:
            console.print(f"Error creating entrypoint: {json_response['detail']}")
            break


@entrypoints_app.command("view")
def entrypoint_get(
    entrypoint_id: Optional[str] = Argument(
        None, help="The UUID of the entrypoint to view."
    ),
):
    provider_guard()
    entrypoint_id = entrypoint_id or EntrypointsManager._select_entrypoint(
        "Please select the entrypoint you want to view"
    )
    response = make_request_with_api_key(
        "GET", f"{V1Routes.ENTRYPOINTS}/{entrypoint_id}"
    )
    json_response = response.json()

    if response.status_code == 200:
        items = [
            (
                str(json_response["id"]),
                json_response["url"],
                json_response["region"]["name"],
            )
        ]
        EntrypointsManager._print_table(items, ["Entrypoint ID", "URL", "Region"])
    else:
        console.print(f"Error getting entrypoint: {json_response['detail']}")


@entrypoints_app.command("update")
def entrypoint_update(
    entrypoint_id: Optional[str] = Argument(
        None, help="The UUID of the entrypoint to update."
    ),
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the update data.",
    ),
):
    provider_guard()
    entrypoint_id = entrypoint_id or EntrypointsManager._select_entrypoint(
        "What's the ID of the entrypoint you want to update?"
    )
    if config_file:
        entrypoint_update = parse_config_file(config_file, EntrypointUpdate)
    else:
        questions = [
            inquirer.Text("url", message="What's the new URL of the entrypoint?")
        ]
        answers = inquirer.prompt(questions)
        entrypoint_update = EntrypointUpdate(url=answers["url"])

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
def entrypoint_delete(
    entrypoint_id: Optional[str] = Argument(
        None, help="The UUID of the entrypoint to delete."
    ),
):
    provider_guard()
    entrypoint_id = entrypoint_id or EntrypointsManager._select_entrypoint(
        "What's the ID of the entrypoint you want to delete?"
    )
    response = make_request_with_api_key(
        "DELETE", f"{V1Routes.ENTRYPOINTS}/{entrypoint_id}"
    )

    if response.status_code == 204:
        console.print(f"Successfully deleted entrypoint {entrypoint_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting entrypoint: {json_response['detail']}")


@entrypoints_app.command("list")
def entrypoint_list(
    offering_id: Optional[str] = Argument(
        None, help="The UUID of the offering to list entrypoints for."
    ),
    limit: int = Option(10, help="Number of entrypoints per page."),
):
    provider_guard()
    offerings = [
        (item["chain"]["name"], item["id"])
        for item in EntrypointsManager._get_offerings()["items"]
    ]
    questions = [
        inquirer.List(
            "offering",
            message="Which offering would you like to list entrypoints for?",
            choices=offerings,
            carousel=True,
        )
    ]
    answers = inquirer.prompt(questions)
    offering_id = offering_id or answers["offering"]
    response = make_request_with_api_key("GET", f"{V1Routes.OFFERINGS}/{offering_id}")
    json_response = response.json()

    if response.status_code == 200:
        entrypoints = json_response["entrypoints"]
        total = len(entrypoints)
        offset = 0

        while True:
            # Paginate entrypoints client-side
            page = entrypoints[offset : offset + limit]
            items = [
                (str(entrypoint["id"]), entrypoint["url"], entrypoint["region"]["name"])
                for entrypoint in page
            ]
            EntrypointsManager._print_table(items, ["Entrypoint ID", "URL", "Region"])

            if not items or len(page) < limit or offset + limit >= total:
                console.print("End of entrypoints list.")
                break

            navigate = inquirer.list_input(
                "Navigate pages", choices=["Next", "Previous", "Exit"], carousel=True
            )

            if navigate == "Next":
                if offset + limit < total:
                    offset += limit
                else:
                    console.print("You are at the end of the list.")
            elif navigate == "Previous":
                if offset - limit >= 0:
                    offset -= limit
                else:
                    console.print("You are at the beginning of the list.")
            else:
                break
    else:
        console.print(f"Error listing entrypoints: {json_response['detail']}")


@entrypoints_app.command("create-internal")
def entrypoint_create_internal(
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the internal provider entrypoint creation data.",
    ),
):
    admin_guard()
    while True:
        if config_file:
            entrypoint_create = parse_config_file(
                config_file, InternalProviderEntrypointCreate
            )
        else:
            chain_id = prompt("Enter the ID of the chain for the entrypoint", type=int)
            url = prompt("Enter the URL of the entrypoint")
            identity = prompt("Enter the identity of the internal provider")

            entrypoint_create = InternalProviderEntrypointCreate(
                url=url, chain_id=chain_id, identity=identity
            )

        response = make_request_with_api_key(
            "POST",
            V1Routes.INTERNAL_PROVIDER_ENTRYPOINTS,
            entrypoint_create.model_dump_json(),
        )
        json_response = response.json()

        if response.status_code == 201:
            console.print("Your internal provider entrypoint has been created.")
            create_another = inquirer.confirm(
                "Would you like to create another entrypoint?"
            )
            if not create_another:
                break
        else:
            console.print(f"Error creating entrypoint: {json_response['detail']}")
            break


@entrypoints_app.command("update-internal")
def entrypoint_update_internal(
    entrypoint_id: Optional[str] = Argument(
        None, help="The UUID of the entrypoint to update."
    ),
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the update data.",
    ),
):
    admin_guard()
    entrypoint_id = entrypoint_id or EntrypointsManager._select_internal_entrypoint(
        "What's the ID of the entrypoint you want to update?"
    )
    if config_file:
        entrypoint_update = parse_config_file(
            config_file, InternalProviderEntrypointUpdate
        )
    else:
        url = prompt("Enter the updated URL of the entrypoint", default=None)
        identity = prompt("Enter the updated identity of the entrypoint", default=None)

        entrypoint_update = InternalProviderEntrypointUpdate(url=url, identity=identity)

    print(entrypoint_id)
    print(entrypoint_update.model_dump_json())
    response = make_request_with_api_key(
        "PATCH",
        f"{V1Routes.INTERNAL_PROVIDER_ENTRYPOINTS}/{entrypoint_id}",
        entrypoint_update.model_dump_json(),
    )
    json_response = response.json()

    if response.status_code == 200:
        console.print("Your internal provider entrypoint has been updated.")
    else:
        console.print(f"Error updating entrypoint: {json_response['detail']}")


@entrypoints_app.command("list-internal")
def entrypoint_list_internal(
    limit: int = Option(10, help="Number of entrypoints per page."),
):
    admin_guard()

    internal_entrypoints = [
        (item["id"], str(item["chain_id"]), item["url"], item["identity"])
        for item in EntrypointsManager._get_internal_provider_entrypoints()["items"]
    ]

    # Print table of internal entrypoints
    EntrypointsManager._print_table(
        internal_entrypoints, ["Entrypoint ID", "Chain ID", "URL", "Identity"]
    )
