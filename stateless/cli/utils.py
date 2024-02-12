import os
import platform
from typing import Type

import httpx
import ujson
from pydantic import BaseModel, ValidationError
from rich.console import Console
from rich.table import Table
from typer import Exit, secho

from .routes import V1Routes

console = Console()

CHAINS_MAPPING = {
    1: "ethereum",
    137: "polygon",
    10: "optimism",
    42161: "arbitrum-one"
}


class BaseManager:
    console = Console()

    @staticmethod
    def make_paginated_request(route: str, offset=0, limit=10, params={}):
        params = {"offset": offset, "limit": limit, **params}
        response = make_request_with_api_key("GET", route, params=params)
        return response.json()

    @staticmethod
    def _print_table(items, columns):
        table = Table(show_header=True, header_style="green", padding=(0, 1, 0, 1))
        for col in columns:
            table.add_column(col)

        for item in items:
            table.add_row(*item, end_section=True)

        console.print(table)


def get_api_key_from_env():
    api_key = os.environ.get("STATELESS_API_KEY")
    if not api_key:
        secho(
            "API key not found in environment variables! Please set your API key in the environment variable STATELESS_API_KEY.",
            fg="red",
        )
        return
    return api_key


def get_route_by_chain_id(chain_id: int):
    return CHAINS_MAPPING[chain_id]


def get_account_type():
    response = make_request_with_api_key("GET", V1Routes.ACCOUNT_PROFILE)
    json_response = response.json()

    if response.status_code == 200:
        return json_response["account_type"]


def provider_guard():
    if get_account_type() != "provider":
        console.print("You must be logged in as a provider to use this command.")
        raise Exit()


def user_guard():
    if get_account_type() != "user":
        console.print("You must be logged in as a user to use this command.")
        raise Exit()


def make_request_with_api_key(
    method: str, url: str, data: str = None, params: dict = None
) -> httpx.Response:
    api_key = get_api_key_from_env()
    headers = {"X-API-KEY": api_key}
    try:
        with httpx.Client() as client:
            if method == "GET":
                response = client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = client.post(url, headers=headers, content=data)
            elif method == "DELETE":
                response = client.delete(url, headers=headers)
            elif method == "PATCH":
                response = client.patch(url, headers=headers, content=data)
            elif method == "PUT":
                response = client.put(url, headers=headers, content=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

        if response.status_code not in (200, 201, 204):
            console.print(f"Error: {response.text}")
            response.raise_for_status()

        return response
    except httpx.HTTPError:
        raise Exit(1)


def parse_config_file(file_path: str, model: Type[BaseModel]) -> Type[BaseModel]:
    with open(file_path) as f:
        json_data = ujson.load(f)

    try:
        validated_data = model.model_validate(json_data)
    except ValidationError as e:
        console.print(f"Error: {e}")
        raise Exit(1)

    return validated_data


def handle_response(response: httpx.Response, success_message, error_message):
    json_response = response.json()
    if response.status_code in [200, 201, 204]:
        console.print(success_message.format(**json_response))
    else:
        console.print(f"{error_message}: {json_response['detail']}")
        raise Exit(1)  # Exit with an error status


def clear_console():
    system_platform = platform.system()

    if system_platform == "Windows":
        os.system("cls")
    else:
        os.system("clear")
