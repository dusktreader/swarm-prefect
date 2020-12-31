import time

import buzz
import requests
from loguru import logger


class SwarmPrefectError(buzz.Buzz):
    ...


def snooze(message, delay=1.0):
    logger.info(message)
    time.sleep(1.0)


def wait_for_client(client, require_tenant=True):
    while True:
        logger.info("Attempting to ping the API")
        with SwarmPrefectError.handle_errors(
            "No response",
            exception_class=requests.exceptions.ConnectionError,
            re_raise=False,
            do_except=lambda e, m, t: snooze("Can't hit the api yet. Still waiting..."),
        ):
            client.graphql("query{hello}", retry_on_api_error=False)
            logger.info("Successfully hit the API. Moving on...")
            break

    if not require_tenant:
        return

    while True:
        logger.info("Checking the API for a tenant")
        with SwarmPrefectError.handle_errors(
            "get_available_tenants() failed",
            re_raise=False,
            do_except=lambda e, m, t: snooze(
                "Call to get_available_tenants() failed. API still isn't ready..."
            ),
        ):
            tenants = client.get_available_tenants()
            break

    while True:
        if not tenants:
            snooze("No tenant yet. Still waiting...")
            tenants = client.get_available_tenants()
        else:
            logger.info("There's the tenant. Now, the client is ready")
            break
