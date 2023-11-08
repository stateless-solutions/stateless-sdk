import typer
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file, handle_api_response
from cli.models.users import UserCreate

console = Console()
users_app = typer.Typer()


def prompt_for_user_create() -> UserCreate:
    try:
        oauth_id = typer.prompt("OAuth2 Unique Identifier")
        username = typer.prompt("Username")
        name = typer.prompt("Name (optional)", default=None)
        email = typer.prompt("Email address (optional)", default=None)
        return UserCreate(oauth_id=oauth_id, username=username, name=name, email=email)
    except ValidationError as e:
        console.print(f"Validation Error: {e}")
        raise typer.Abort()


@users_app.command("create")
def create_user(
    config_file: str = typer.Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the user creation data.",
    )
):
    try:
        if config_file:
            user_create = parse_config_file(config_file, UserCreate)
        else:
            user_create = prompt_for_user_create()
        response = make_request_with_api_key("POST", V1Routes.USERS, user_create.json())
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@users_app.command("current")
def get_current_user():
    try:
        response = make_request_with_api_key("GET", V1Routes.CURRENT_USER)
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@users_app.command("get")
def get_user(user_id: str = typer.Argument(..., help="The ID of the user to get.")):
    try:
        response = make_request_with_api_key("GET", f"{V1Routes.USERS}/{user_id}")
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@users_app.command("list")
def list_users():
    try:
        response = make_request_with_api_key("GET", V1Routes.LIST_USERS)
        users = response.json()["items"]
        table = Table(show_header=True, header_style="green")
        table.add_column("ID")
        table.add_column("Name")

        for item in users:
            table.add_row(item["id"], item["name"])
        console.print(table)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


@users_app.command("delete")
def delete_user(
    user_id: str = typer.Argument(..., help="The ID of the user to delete.")
):
    try:
        response = make_request_with_api_key("DELETE", f"{V1Routes.USERS}/{user_id}")
        handle_api_response(response)
    except Exception as e:
        console.print(f"Unexpected error: {e}", style="bold red")
        raise typer.Abort()


if __name__ == "__main__":
    users_app()
