from typing import Optional

from rich.console import Console
from rich.table import Table
from typer import Argument, Option, Typer, prompt

from ..models.users import UserCreate
from ..routes import V1Routes
from ..utils import make_request_with_api_key, parse_config_file

console = Console()
users_app = Typer()


@users_app.command("create")
def create_user(
    config_file: Optional[str] = Option(
        None,
        "--config-file",
        "-c",
        help="The path to a JSON file with the user creation data.",
    ),
):
    if config_file:
        user_create = parse_config_file(config_file, UserCreate)
    else:
        oauth_id = prompt("Enter OAuth2 Unique Identifier")
        status = prompt("Enter Account Status", default="active")
        email = prompt("Enter Email Address", default=None)
        name = prompt("Enter Name", default=None)
        username = prompt("Enter Username")

        user_create = UserCreate(
            oauth_id=oauth_id, status=status, email=email, name=name, username=username
        )

    response = make_request_with_api_key(
        "POST", V1Routes.USERS, user_create.model_dump_json()
    )
    json_response = response.json()

    if response.status_code == 201:
        console.print(f"Successfully created user {json_response['id']}")
    else:
        console.print(f"Error creating user: {json_response['detail']}")


@users_app.command("current")
def get_current_user():
    response = make_request_with_api_key("GET", V1Routes.CURRENT_USER)
    json_response = response.json()

    if response.status_code == 200:
        console.print(json_response)
    else:
        console.print(f"Error getting current user: {json_response['detail']}")


@users_app.command("view")
def get_user(
    user_id: Optional[str] = Argument(None, help="The ID of the user to view.")
):
    if not user_id:
        user_id = prompt("Enter the ID of the user to view")

    response = make_request_with_api_key("GET", f"{V1Routes.USERS}/{user_id}")
    json_response = response.json()

    if response.status_code == 200:
        console.print(json_response)
    else:
        console.print(f"Error getting user: {json_response['detail']}")


@users_app.command("list")
def list_users():
    response = make_request_with_api_key("GET", V1Routes.LIST_USERS)

    json_response = response.json()

    table = Table(show_header=True, header_style="green")
    table.add_column("ID")
    table.add_column("Name")

    for item in json_response["items"]:
        table.add_row(item["id"], item["name"])

    console.print(table)


@users_app.command("delete")
def delete_user(
    user_id: Optional[str] = Argument(None, help="The ID of the user to delete.")
):
    if not user_id:
        user_id = prompt("Enter the ID of the user to delete")

    response = make_request_with_api_key("DELETE", f"{V1Routes.USERS}/{user_id}")

    if response.status_code == 204:
        console.print(f"Successfully deleted user {user_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting user: {json_response['detail']}")
