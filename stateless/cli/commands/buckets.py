from typing import Optional

import inquirer
from rich.console import Console
from typer import Argument, Option, Typer

from ..models.buckets import BucketCreate, BucketUpdate
from ..routes import V1Routes
from ..utils import (
    BaseManager,
    get_route_by_chain_id,
    make_request_with_api_key,
    parse_config_file,
    user_guard,
)
from .offerings import OfferingsManager

console = Console()
buckets_app = Typer()


class BucketsManager(BaseManager):
    @staticmethod
    def _get_buckets(offset=0, limit=10):
        return BucketsManager.make_paginated_request(
            V1Routes.LIST_BUCKETS, offset, limit
        )

    @staticmethod
    def _select_bucket(prompt_message):
        offset = 0
        limit = 10
        selected_bucket = None
        while selected_bucket is None:
            response = BucketsManager._get_buckets(offset=offset, limit=limit)
            buckets = response.get("items", [])
            total = response.get("total", 0)

            if not buckets and offset == 0:  # No buckets available at all
                console.print("No buckets available.")
                return None

            bucket_choices = [(bucket["name"], bucket["id"]) for bucket in buckets]
            navigation_message = ""
            # Add navigation choices if applicable
            if offset > 0:
                bucket_choices.insert(0, ("Previous Page", "prev"))
                navigation_message += "[bold yellow]Previous Page: Go back to the previous page.[/bold yellow]"
            if total > offset + limit:
                bucket_choices.append(("Next Page", "next"))
                # Apply yellow color specifically to the "Next Page" message
                navigation_message += "[bold yellow]Next Page: Move to the next page of buckets.[/bold yellow]"

            if navigation_message:
                console.print(navigation_message, style="bold cyan")

            questions = [
                inquirer.List(
                    "bucket_id",
                    message=prompt_message,
                    choices=bucket_choices,
                    carousel=True
                )
            ]
            answers = inquirer.prompt(questions)
            choice = answers["bucket_id"]

            if choice == "next":
                offset += limit
            elif choice == "prev":
                offset = max(0, offset - limit)
            else:
                selected_bucket = next((bucket for bucket in buckets if bucket["id"] == choice), None)

        return selected_bucket


@buckets_app.command("list")
def buckets_list(limit: int = Option(10, help="Number of buckets per page.")):
    user_guard()
    offset = 0
    while True:
        response = BucketsManager._get_buckets(offset=offset, limit=limit)
        buckets = response["items"]
        total = response.get("total", len(buckets))

        if not buckets:
            console.print(
                "You've got no buckets! You can create one with `stateless-cli buckets create`."
            )
            break

        items = [
            (
                bucket["id"],
                bucket["name"],
                bucket["chain"]["name"],
                "\n".join(
                    [
                        f"{offering['provider']['name']} "
                        + " ".join(
                            [
                                f"{region}[{count}]"
                                for region, count in {
                                    entrypoint["region"]["name"]: len(
                                        [
                                            ep
                                            for ep in offering["entrypoints"]
                                            if ep["region"]["name"]
                                            == entrypoint["region"]["name"]
                                        ]
                                    )
                                    for offering in bucket["offerings"]
                                    for entrypoint in offering["entrypoints"]
                                }.items()
                            ]
                        )
                        for offering in bucket["offerings"]
                    ]
                ),
                f"https://api.stateless.solutions/{get_route_by_chain_id(int(bucket['chain_id']))}/v1/{bucket['id']}",
            )
            for bucket in buckets
        ]

        BucketsManager._print_table(items, ["ID", "Name", "Chain", "Offerings", "URL"])

        if len(buckets) < limit or offset + limit >= total:
            console.print("End of buckets list.")
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


@buckets_app.command("create")
def buckets_create(config_file: Optional[str] = Option(None, "--config_file", "-c")):
    user_guard()
    while True:
        if config_file:
            bucket_create = parse_config_file(config_file, BucketCreate)
        else:
            response = make_request_with_api_key("GET", V1Routes.CHAINS)
            chains = [
                (str(item["name"]), str(item["chain_id"]))
                for item in response.json()["items"]
            ]
            questions = [
                inquirer.Text("name", message="Enter the name of the bucket"),
                inquirer.List(
                    "chain_id",
                    message="Choose a blockchain for this bucket",
                    choices=chains,
                    carousel=True,
                ),
            ]
            answers = inquirer.prompt(questions)

            name = answers["name"]
            chain_id = answers["chain_id"]

            offering_ids = OfferingsManager._select_offerings(
                "Choose the offerings to associate with the bucket", int(chain_id)
            )
            bucket_create = BucketCreate(
                name=name, chain_id=chain_id, offerings=offering_ids
            )

        response = make_request_with_api_key(
            "POST", V1Routes.BUCKETS, bucket_create.model_dump_json()
        )
        json_response = response.json()

        if response.status_code == 201:
            chain_route = get_route_by_chain_id(int(chain_id))
            console.print(
                f"Your bucket has been created, and your URL is: https://api.stateless.solutions/{chain_route}/v1/{json_response['id']}"
            )
            create_another = inquirer.confirm(
                "Would you like to create another bucket?"
            )
            if not create_another:
                break
        else:
            console.print(f"Error creating bucket: {json_response['detail']}")
            break


@buckets_app.command("update")
def buckets_update(
    bucket_id: Optional[str] = Argument(None, help="The UUID of the bucket to update."),
    config_file: Optional[str] = Option(None, "--config-file", "-c"),
):
    user_guard()
    if not bucket_id:
        bucket = BucketsManager._select_bucket("Choose the bucket to update")
        bucket_id = bucket["id"]
        bucket_name = bucket["name"]
        bucket_chain_id = bucket["chain"]["chain_id"]
        bucket_offerings_ids = [offering["id"] for offering in bucket["offerings"]]

    if config_file:
        bucket_update = parse_config_file(config_file, BucketUpdate)
    else:
        name = inquirer.text(
            message="Enter the updated name of the bucket", default=bucket_name
        )
        offering_ids = OfferingsManager._select_offerings(
            "Choose the offerings to associate with the bucket",
            int(bucket_chain_id),
            bucket_offerings_ids,
        )
        bucket_update = BucketUpdate(name=name, offerings=offering_ids)

    response = make_request_with_api_key(
        "PATCH", f"{V1Routes.BUCKETS}/{bucket_id}", bucket_update.model_dump_json()
    )
    json_response = response.json()

    if response.status_code == 200:
        console.print(f"Successfully updated bucket {json_response['id']}")
    else:
        console.print(f"Error updating bucket: {json_response['detail']}")


@buckets_app.command("view")
def buckets_get(
    bucket_id: Optional[str] = Argument(None, help="The UUID of the bucket to view."),
):
    user_guard()
    if not bucket_id:
        bucket = BucketsManager._select_bucket("Choose the bucket to view")
        bucket_id = bucket["id"]

    response = make_request_with_api_key("GET", f"{V1Routes.BUCKETS}/{bucket_id}")
    json_response = response.json()

    if response.status_code == 200:
        # Display table with bucket info
        items = [
            (
                bucket["id"],
                bucket["name"],
                bucket["chain"]["name"],
                "\n".join(
                    [
                        f"{offering['provider']['name']} [{', '.join([entrypoint['region']['name'] for entrypoint in offering['entrypoints']])}]"
                        for offering in bucket["offerings"]
                    ]
                ),
                f"https://api.stateless.solutions/{get_route_by_chain_id(int(bucket['chain_id']))}/v1/{bucket['id']}",
            )
            for bucket in [json_response]
        ]

        BucketsManager._print_table(items, ["ID", "Name", "Chain", "Offerings", "URL"])
    else:
        console.print(f"Error getting bucket: {json_response['detail']}")


@buckets_app.command("delete")
def buckets_delete(
    bucket_id: Optional[str] = Argument(None, help="The UUID of the bucket to delete."),
):
    user_guard()
    if not bucket_id:
        bucket = BucketsManager._select_bucket("Choose the bucket to delete")
        bucket_id = bucket["id"]

    response = make_request_with_api_key("DELETE", f"{V1Routes.BUCKETS}/{bucket_id}")

    if response.status_code == 204:
        console.print(f"Successfully deleted bucket {bucket_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting bucket: {json_response['detail']}")
