import webbrowser
from typing import Annotated, Optional

import httpx
from typer import Context, Exit, Option, Typer, confirm, secho

from .cli.commands.api_keys import api_keys_app
from .cli.commands.buckets import buckets_app
from .cli.commands.chains import chains_app
from .cli.commands.entrypoints import entrypoints_app
from .cli.commands.offerings import offerings_app
from .cli.commands.providers import providers_app
from .cli.commands.regions import regions_app
from .cli.commands.users import users_app
from .cli.routes import V1Routes
from .cli.utils import get_api_key_from_env, make_request_with_api_key

app = Typer()
app.add_typer(offerings_app, name="offerings")
app.add_typer(entrypoints_app, name="entrypoints")
app.add_typer(buckets_app, name="buckets")
app.add_typer(api_keys_app, name="api-keys")
app.add_typer(users_app, name="users")
app.add_typer(providers_app, name="providers")
app.add_typer(chains_app, name="chains")
app.add_typer(regions_app, name="regions")


ascii_art = r"""
   _____ _        _       _                  _____ _      _____ 
  / ____| |      | |     | |                / ____| |    |_   _|
 | (___ | |_ __ _| |_ ___| | ___  ___ ___  | |    | |      | |  
  \___ \| __/ _` | __/ _ \ |/ _ \/ __/ __| | |    | |      | |  
  ____) | || (_| | ||  __/ |  __/\__ \__ \ | |____| |____ _| |_ 
 |_____/ \__\__,_|\__\___|_|\___||___/___/  \_____|______|_____|                                                        
"""  # noqa: W291

__version__ = "0.0.11"  # Keep this in sync with pyproject.toml


def version_callback(value: bool):
    if value:
        print(f"Stateless CLI Version: {__version__}")
        raise Exit()


def latest_version_callback():
    with httpx.Client() as client:
        response = client.get("https://pypi.org/pypi/stateless-sdk/json")
        version = response.json()["info"]["version"]

        if version != __version__:
            secho(f"New version available: {version}", fg="yellow")
            secho("Run `pip install stateless-sdk --upgrade` to update", fg="yellow")


@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    version: Annotated[
        Optional[bool], Option("--version", callback=version_callback)
    ] = None,
):
    if ctx.invoked_subcommand is None:
        # ASCII Art Logo
        secho(ascii_art, fg="green")
        latest_version_callback()

        if not get_api_key_from_env():
            if confirm("Do you need an API key to proceed?"):
                secho(
                    "Redirecting to the API key registration page, afterwards please add it to your environment variables...",
                    fg="red",
                )
                webbrowser.open("https://app.stateless.solutions")
        else:
            latest_version_callback()
            response = make_request_with_api_key("GET", V1Routes.ACCOUNT_PROFILE)
            json_response = response.json()

            if response.status_code == 200:
                name: str = json_response["name"]
                account_type: str = json_response["account_type"]
                secho("You are logged in as: ", nl=False)
                secho(f"{name} [{account_type.capitalize()}]", fg="yellow")
                secho(
                    "Explore our commands by running `stateless-cli --help`",
                    fg="green",
                )
            else:
                secho(
                    f"Error getting account profile: {json_response['detail']}",
                    fg="red",
                )


def _main():
    app()


if __name__ == "__main__":
    _main()
