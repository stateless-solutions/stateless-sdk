import typer
from typing import Optional
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file, handle_api_response
from cli.models.buckets import BucketCreate, BucketUpdate

console = Console()
buckets_app = typer.Typer()


def prompt_for_bucket_create() -> BucketCreate:
    try:
        user_id = typer.prompt("User ID (Admins only)", default=None)
        name = typer.prompt("Bucket Name")
        chain_id = typer.prompt("Chain ID", type=int)
        offerings = typer.prompt("Offerings (comma-separated UUIDs)", default="")
        offerings_list = offerings.split(",") if offerings else []
        return BucketCreate(
            user_id=user_id, name=name, chain_id=chain_id, offerings=offerings_list
        )
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


def prompt_for_bucket_update() -> BucketUpdate:
    try:
        name = typer.prompt("Bucket Name", default=None)
        offerings = typer.prompt("Offerings (comma-separated UUIDs)", default=None)
        offerings_list = offerings.split(",") if offerings else None
        return BucketUpdate(name=name, offerings=offerings_list)
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


@buckets_app.command("list")
def buckets_list():
    try:
        response = make_request_with_api_key("GET", V1Routes.LIST_BUCKETS)
        if response.status_code == 200:
            buckets = response.json()
            table = Table(show_header=True, header_style="bold green")
            table.add_column("ID", style="dim")
            table.add_column("Name")
            table.add_column("Chain")
            table.add_column("Offering IDs")

            for item in buckets["items"]:
                entrypoint_id = item["id"]
                bucket_name = item["name"]
                chain_name = item.get("chain", {}).get(
                    "name", "N/A"
                )  # Fallback to N/A if chain or name is not present
                offering_ids = [
                    offering["id"] for offering in item.get("offerings", [])
                ]
                offerings = "\n".join(offering_ids)
                table.add_row(entrypoint_id, bucket_name, chain_name, offerings)

            console.print(table)
        else:
            console.print(
                f"Error retrieving buckets: {response.text}", style="bold red"
            )
            raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@buckets_app.command("create")
def buckets_create(
    config_file: Optional[str] = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the bucket creation data.",
    )
):
    try:
        if config_file:
            bucket_create = parse_config_file(config_file, BucketCreate)
        else:
            bucket_create = prompt_for_bucket_create()
        response = make_request_with_api_key(
            "POST", V1Routes.BUCKETS, bucket_create.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@buckets_app.command("update")
def buckets_update(
    bucket_id: str = typer.Argument(..., help="The UUID of the bucket to update."),
    config_file: Optional[str] = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the update data.",
    ),
):
    try:
        if config_file:
            bucket_update = parse_config_file(config_file, BucketUpdate)
        else:
            bucket_update = prompt_for_bucket_update()
        response = make_request_with_api_key(
            "PATCH", f"{V1Routes.BUCKETS}/{bucket_id}", bucket_update.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@buckets_app.command("get")
def buckets_get(
    bucket_id: str = typer.Argument(..., help="The UUID of the bucket to get.")
):
    try:
        response = make_request_with_api_key("GET", f"{V1Routes.BUCKETS}/{bucket_id}")
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@buckets_app.command("delete")
def buckets_delete(
    bucket_id: str = typer.Argument(..., help="The UUID of the bucket to delete.")
):
    try:
        response = make_request_with_api_key(
            "DELETE", f"{V1Routes.BUCKETS}/{bucket_id}"
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()
