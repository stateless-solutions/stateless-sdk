from typer import Typer, Option, Argument
from rich.console import Console
from rich.table import Table
from cli.routes import V1Routes
from cli.utils import make_request_with_api_key, parse_config_file

from cli.types.users import UserCreate

console = Console()
users_app = Typer()


@users_app.command("create")
def create_user(
    config_file: str = Option(
        ..., help="The path to a JSON file with the user creation data."
    )
):
    user_create = parse_config_file(config_file, UserCreate)
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


@users_app.command("get")
def get_user(user_id: str = Argument(..., help="The ID of the user to get.")):
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
    # Add more columns as needed

    for item in json_response["items"]:
        table.add_row(item["id"], item["name"])  # Add more columns as needed

    console.print(table)


@users_app.command("delete")
def delete_user(user_id: str = Argument(..., help="The ID of the user to delete.")):
    response = make_request_with_api_key("DELETE", f"{V1Routes.USERS}/{user_id}")

    if response.status_code == 204:
        console.print(f"Successfully deleted user {user_id}")
    else:
        json_response = response.json()
        console.print(f"Error deleting user: {json_response['detail']}")