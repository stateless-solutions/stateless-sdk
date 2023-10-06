import webbrowser
import time
from typer import Typer, secho, confirm

from cli.commands.offerings import offerings_app
from cli.commands.entrypoints import entrypoints_app
from cli.commands.buckets import buckets_app
from cli.commands.api_keys import api_keys_app
from cli.commands.users import users_app
from cli.commands.providers import providers_app
from cli.commands.chains import chains_app
from cli.commands.regions import regions_app
from cli.utils import get_api_key_from_env

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


@app.command("setup")
def main():
    # ASCII Art Logo
    secho(ascii_art, fg="green")

    secho("Welcome to the Stateless CLI!", fg="blue")

    while True:
        has_api_key = confirm("Do you have an API key to proceed?")

        if not has_api_key:
            secho("Redirecting to the API key registration page...", fg="red")
            webbrowser.open("https://app.stateless.solutions")
            secho("Waiting for a few seconds before asking again...", fg="yellow")
            time.sleep(5)
        else:
            api_key = get_api_key_from_env()
            if not api_key:
                secho(
                    "Please set your API key in the environment variable STATELESS_API_KEY."
                )
            else:
                secho("API key found! Feel free to use commands now!", fg="green")

            break


if __name__ == "__main__":
    app()
