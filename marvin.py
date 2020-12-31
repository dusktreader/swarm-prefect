import os

import click
import prefect
import prefect_server.cli.database

from helpers import SwarmPrefectError, logger, wait_for_client


def ascii_welcome(ui_port="8080"):
    ui_url = click.style(
        f"http://localhost:{ui_port}", fg="white", bg="blue", bold=True
    )
    docs_url = click.style("https://docs.prefect.io", fg="white", bg="blue", bold=True)

    with open("/banner.txt") as banner_file:
        title = banner_file.read()

    message = f"""
    {click.style('WELCOME TO', fg='blue', bold=True)}\n{click.style(title, bold=True)}
    Visit {ui_url} to get started, or check out the docs at {docs_url}
    """

    return message


logger.info("Just here to do my ghastly start up duties")
apollo_host = os.environ["APOLLO_URL"]
with prefect.utilities.configuration.set_temporary_config({
    "cloud.api": apollo_host,
    "cloud.graphql": f"{apollo_host}/graphql",
    "backend": "server",
}):
    client = prefect.Client()
    wait_for_client(client, require_tenant=False)

    logger.info("Now I have to prepare the database. What a challenge...")
    with SwarmPrefectError.handle_errors(
        "Oh, it failed. Shocking",
        do_except=lambda e, m, t: logger.error(m),
        re_raise=True,
    ):
        prefect_server.cli.database.alembic_upgrade()

    if not client.get_available_tenants():
        logger.info("Sure, I'll create a defult tenant, but I won't enjoy it")
        client.create_tenant(name="default")

    logger.info("Now I have to show the welcome banner. How ghastly:")
    logger.info(ascii_welcome(ui_port=os.environ.get("UI_HOST_PORT", "8080")))
