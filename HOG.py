import os
import prefect
from helpers import SwarmPrefectError, logger, wait_for_client


logger.info("Setting up cargo of workflows")
apollo_host = os.environ["APOLLO_URL"]
with prefect.utilities.configuration.set_temporary_config(
    {
        "cloud.api": apollo_host,
        "cloud.graphql": f"{apollo_host}/graphql",
        "backend": "server",
    }
):
    project_name = os.environ.get("PROJECT_NAME")
    SwarmPrefectError.require_condition(
        project_name,
        "No PROJECT_NAME found environment. Probability of success 0%",
    )

    with SwarmPrefectError.handle_errors(
            "Given this explosion in engineering, probability of success is 0%",
            do_except=lambda e, m, t: logger.info(m),
            re_raise=True,
    ):
        client = prefect.Client()
        wait_for_client(client)

        project_query = {
            "query": {
                prefect.utilities.graphql.with_args(
                    "project", {"where": {"name": {"_eq": project_name}}}
                ): {"id": True}
            }
        }
        project_query_results = client.graphql(project_query)
        SwarmPrefectError.require_condition(
            project_query_results,
            "Query for project name failed in a most improbable way",
        )

        if len(project_query_results['data']['project']) == 0:
            logger.info(f"Couldn't find project {project_name}. Improbably creating it")
            client.create_project(project_name=project_name)

        logger.info("Registering fetched flows")
        from flows import all_flows

        for flow in all_flows:
            flow.register(project_name=project_name)
        logger.info("All done!")
