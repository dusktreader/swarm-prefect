"""
Note: This is not related AT ALL to our crappy instant messenger client. It's rather
one of the 4 main characters from __Hitchiker's Guide To the Galaxy__ which is the
basis for the theme of the Prefect project
"""

import os
import prefect
import docker
from helpers import SwarmPrefectError, logger, wait_for_client


logger.info("Starting up an agent")
apollo_host = os.environ["APOLLO_URL"]
with prefect.utilities.configuration.set_temporary_config(
    {
        "cloud.api": apollo_host,
        "cloud.graphql": f"{apollo_host}/graphql",
        "backend": "server",
    }
):
    with SwarmPrefectError.handle_errors(
            "Well, that didn't work at all!",
            do_except=lambda e, m, t: logger.info(m),
            re_raise=True,
    ):
        client = prefect.Client()
        wait_for_client(client)

        logger.info("Starting a docker agent...")
        prefect.agent.docker.DockerAgent(
            show_flow_logs=True,
            docker_interface=False,
            network="prefect-server",
            base_url="tcp://zaphod:2375",
        ).start()
        logger.info("All done!")
