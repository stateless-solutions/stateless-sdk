import ujson
from typer import Typer, Option, Argument
from rich.console import Console
from rich.table import Table

from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file

from cli.models.buckets import BucketCreate, BucketUpdate

console = Console()
buckets_app = Typer()


@buckets_app.command("list")
def buckets_list():
    response = make_request_with_api_key("GET", V1Routes.LIST_BUCKETS)
    buckets = response.json()

    # TODO: fix joined loads so we display provider/offerings name instead of IDs
    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Name")
    table.add_column("Chain")
    table.add_column("Offering IDs")

    for item in buckets["items"]:
        entrypoint_id = item["id"]
        bucket_name = item["name"]
        chain_name = item["chain"]["name"]
        offering_ids = [buckets["id"] for buckets in item["offerings"]]
        offerings = "\n".join(offering_ids)
        table.add_row(entrypoint_id, bucket_name, chain_name, str(offerings))

    console.print(table)


@buckets_app.command("create")
def buckets_create(config_file: str = Option()):
    bucket_create = parse_config_file(config_file, BucketCreate)
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
    bucket_id: str = Argument(..., help="The UUID of the bucket to update."),
    config_file: str = Option(
        ..., help="The path to a JSON file with the update data."
    ),
):
    bucket_update = parse_config_file(config_file, BucketUpdate)
    response = make_request_with_api_key(
        "PATCH", f"{V1Routes.BUCKETS}/{bucket_id}", bucket_update.model_dump_json()
    )

    json_response = response.json()

    if response.status_code == 200:
        console.print(f"Successfully updated bucket {json_response['id']}")
    else:
        console.print(f"Error updating bucket: {json_response['detail']}")


@buckets_app.command("get")
def buckets_get(bucket_id: str = Argument(..., help="The UUID of the bucket to get.")):
    response = make_request_with_api_key("GET", f"{V1Routes.BUCKETS}/{bucket_id}")

    json_response = response.json()

    if response.status_code == 200:
        console.print(ujson.dumps(json_response, indent=2))
    else:
        console.print(f"Error getting bucket: {json_response['detail']}")


@buckets_app.command("delete")
def buckets_delete(
    bucket_id: str = Argument(..., help="The UUID of the bucket to delete.")
):
    response = make_request_with_api_key("DELETE", f"{V1Routes.BUCKETS}/{bucket_id}")

    if response.status_code == 204:
        console.print(f"Successfully deleted bucket {bucket_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting bucket: {json_response['detail']}")
