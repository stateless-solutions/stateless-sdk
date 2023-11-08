import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file, handle_api_response
from cli.models.entrypoints import EntrypointCreate, EntrypointUpdate

console = Console()
entrypoints_app = typer.Typer()


def prompt_for_entrypoint_create() -> EntrypointCreate:
    try:
        url = typer.prompt("Entrypoint URL")
        offering_id = typer.prompt("Offering ID")
        region_id = typer.prompt("Region ID")
        return EntrypointCreate(url=url, offering_id=offering_id, region_id=region_id)
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


def prompt_for_entrypoint_update() -> EntrypointUpdate:
    try:
        url = typer.prompt("Updated Entrypoint URL", default=None)
        return EntrypointUpdate(url=url)
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


@entrypoints_app.command("list")
def entrypoint_list():
    try:
        response = make_request_with_api_key("GET", V1Routes.LIST_ENTRYPOINTS)
        if response.status_code == 200:
            entrypoints = response.json()
            table = Table(show_header=True, header_style="bold green")
            table.add_column("ID", style="dim")
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
        else:
            console.print(
                f"Error retrieving entrypoints: {response.text}", style="bold red"
            )
            raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@entrypoints_app.command("create")
def entrypoint_create(
    config_file: str = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the entrypoint creation data.",
    )
):
    try:
        if config_file:
            entrypoint_create = parse_config_file(config_file, EntrypointCreate)
        else:
            entrypoint_create = prompt_for_entrypoint_create()
        response = make_request_with_api_key(
            "POST", V1Routes.ENTRYPOINTS, entrypoint_create.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@entrypoints_app.command("update")
def entrypoint_update(
    entrypoint_id: str = typer.Argument(
        None, help="The UUID of the entrypoint to update."
    ),
    config_file: str = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the update data.",
    ),
):
    try:
        entrypoint_id = entrypoint_id or typer.prompt("Entrypoint ID")
        if config_file:
            entrypoint_update = parse_config_file(config_file, EntrypointUpdate)
        else:
            entrypoint_update = prompt_for_entrypoint_update()
        response = make_request_with_api_key(
            "PATCH", f"{V1Routes.ENTRYPOINTS}/{entrypoint_id}", entrypoint_update.json()
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@entrypoints_app.command("get")
def entrypoint_get(
    entrypoint_id: str = typer.Argument(None, help="The UUID of the entrypoint to get.")
):
    try:
        entrypoint_id = entrypoint_id or typer.prompt("Entrypoint ID")
        response = make_request_with_api_key(
            "GET", f"{V1Routes.ENTRYPOINTS}/{entrypoint_id}"
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@entrypoints_app.command("delete")
def entrypoint_delete(
    entrypoint_id: str = typer.Argument(
        None, help="The UUID of the entrypoint to delete."
    )
):
    try:
        entrypoint_id = entrypoint_id or typer.prompt("Entrypoint ID")
        response = make_request_with_api_key(
            "DELETE", f"{V1Routes.ENTRYPOINTS}/{entrypoint_id}"
        )
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


if __name__ == "__main__":
    entrypoints_app()
