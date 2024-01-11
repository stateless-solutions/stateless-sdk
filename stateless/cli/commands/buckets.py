from typing import Optional

import inquirer
import ujson
from rich.console import Console
from rich.table import Table
from typer import Argument, Option, Typer

from ..models.buckets import BucketCreate, BucketUpdate
from ..routes import V1Routes
from ..utils import make_request_with_api_key, parse_config_file
from .offerings import OfferingsManager

console = Console()
buckets_app = Typer()


class BucketsManager:
    @staticmethod
    def _get_buckets():
        response = make_request_with_api_key("GET", V1Routes.LIST_BUCKETS)
        return response.json()["items"]

    @staticmethod
    def _select_bucket(prompt_message):
        buckets = BucketsManager._get_buckets()
        choices = [(bucket["name"], bucket["id"]) for bucket in buckets]
        questions = [
            inquirer.List(
                "bucket", message=prompt_message, choices=choices, carousel=True
            )
        ]
        answers = inquirer.prompt(questions)
        bucket_id = answers["bucket"]
        chain_id = [bucket["chain_id"] for bucket in buckets if bucket["id"] == bucket_id][0]
        return bucket_id, chain_id

    @staticmethod
    def _print_table(items, columns):
        table = Table(show_header=True, header_style="green", padding=(0, 1, 0, 1))
        for col in columns:
            table.add_column(col)

        for item in items:
            table.add_row(*item, end_section=True)

        console.print(table)


@buckets_app.command("list")
def buckets_list():
    buckets = BucketsManager._get_buckets()
    if not buckets or (isinstance(buckets, list) and len(buckets) == 0):
        console.print("You've got no buckets! You can create one with `stateless-cli buckets create`.")
        return

    items = [
        (
            bucket["id"],
            bucket["name"],
            bucket["chain"]["name"],
            "\n".join([f"{offering['provider']['name']}" for offering in bucket["offerings"]]),
        )
        for bucket in buckets
    ]
    BucketsManager._print_table(items, ["ID", "Name", "Chain", "Offerings"])


@buckets_app.command("create")
def buckets_create(config_file: Optional[str] = Option(None, "--config-file", "-c")):
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
            )
        ]
        answers = inquirer.prompt(questions)

        name = answers["name"]
        chain_id = answers["chain_id"]

        offering_ids = OfferingsManager._select_offerings("Choose the offerings to associate with the bucket", int(chain_id))
        bucket_create = BucketCreate(
            name=name, chain_id=chain_id, offerings=offering_ids
        )

    response = make_request_with_api_key(
        "POST", V1Routes.BUCKETS, bucket_create.model_dump_json()
    )
    json_response = response.json()

    if response.status_code == 201:
        console.print(f"Successfully created bucket {json_response['id']}")
    else:
        console.print(f"Error creating bucket: {json_response['detail']}")


@buckets_app.command("update")
def buckets_update(
    bucket_id: Optional[str] = Argument(None, help="The UUID of the bucket to update."),
    config_file: Optional[str] = Option(None, "--config-file", "-c"),
):
    if not bucket_id:
        bucket_id, chain_id = BucketsManager._select_bucket("Choose the bucket to update")

    if config_file:
        bucket_update = parse_config_file(config_file, BucketUpdate)
    else:
        name = inquirer.text(message="Enter the updated name of the bucket")
        offering_ids = OfferingsManager._select_offerings("Choose the offerings to associate with the bucket", int(chain_id))
        bucket_update = BucketUpdate(name=name, offerings=offering_ids)

    response = make_request_with_api_key(
        "PATCH", f"{V1Routes.BUCKETS}/{bucket_id}", bucket_update.model_dump_json()
    )
    json_response = response.json()

    if response.status_code == 200:
        console.print(f"Successfully updated bucket {json_response['id']}")
    else:
        console.print(f"Error updating bucket: {json_response['detail']}")


@buckets_app.command("get")
def buckets_get(
    bucket_id: Optional[str] = Argument(None, help="The UUID of the bucket to get."),
):
    if not bucket_id:
        bucket_id, _ = BucketsManager._select_bucket("Choose the bucket to get")

    response = make_request_with_api_key("GET", f"{V1Routes.BUCKETS}/{bucket_id}")
    json_response = response.json()

    if response.status_code == 200:
        console.print(ujson.dumps(json_response, indent=2))
    else:
        console.print(f"Error getting bucket: {json_response['detail']}")


@buckets_app.command("delete")
def buckets_delete(
    bucket_id: Optional[str] = Argument(None, help="The UUID of the bucket to delete."),
):
    if not bucket_id:
        bucket_id, _ = BucketsManager._select_bucket("Choose the bucket to delete")

    response = make_request_with_api_key("DELETE", f"{V1Routes.BUCKETS}/{bucket_id}")

    if response.status_code == 204:
        console.print(f"Successfully deleted bucket {bucket_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting bucket: {json_response['detail']}")
