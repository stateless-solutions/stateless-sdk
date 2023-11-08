from typing import Type

import httpx
import ujson
from pydantic import BaseModel, ValidationError

from rich.console import Console
from typer import secho, Exit

console = Console()


def get_api_key_from_env():
    import os

    api_key = os.environ.get("STATELESS_API_KEY")
    if not api_key:
        secho("API key not found in environment variables!", fg="red")
        return

    return api_key


def make_request_with_api_key(
    method: str, url: str, data: str = None
) -> httpx.Response:
    api_key = get_api_key_from_env()
    headers = {"X-API-KEY": api_key}

    with httpx.Client() as client:
        if method == "GET":
            response = client.get(url, headers=headers)
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
        console.print(f"Error: {response.json()}")
        response.raise_for_status()

    return response


def parse_config_file(file_path: str, model: Type[BaseModel]) -> Type[BaseModel]:
    with open(file_path) as f:
        json_data = ujson.load(f)

    try:
        validated_data = model.model_validate(json_data)
    except ValidationError as e:
        console.print(f"Error: {e}")
        raise Exit(1)

    return validated_data


def handle_api_response(response):
    if response.status_code in [200, 201, 204]:
        if response.status_code != 204:  # No content
            json_response = response.json()
            console.print(json_response)
    else:
        console.print(f"Error: {response.text}", style="bold red")
        raise Exit(code=1)
