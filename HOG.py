import os
import prefect
from helpers import SwarmPrefectError, logger, wait_for_client


logger.info("Setting up cargo of workflows")
apollo_host = os.getenv("APOLLO_URL")
with prefect.utilities.configuration.set_temporary_config(
    {
        "cloud.api": apollo_host,
        "cloud.graphql": f"{apollo_host}/graphql",
        "backend": "server",
    }
):
    project_name = os.getenv("PROJECT_NAME")
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

        prefect_version = os.getenv("PREFECT_SERVER_TAG", "latest")
        flow_storage = prefect.storage.s3.S3(
            bucket=os.getenv('S3_FLOW_BUCKET'),
            client_options=dict(
                # this should be a secret eventually
                aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
                # this should be a secret eventually
                aws_secret_access_key=os.getenv('S3_SECRET_KEY'),
                endpoint_url=os.getenv('S3_URL'),
            ),
        )
        for flow in all_flows:
            flow_storage.add_flow(flow)

        built_storage = flow_storage.build()
        for flow in all_flows:
            flow.storage = built_storage
            flow.run_config = prefect.run_configs.DockerRun(
                image=f"prefecthq/prefect:{prefect_version}",
            )
            flow.result = prefect.engine.results.s3_result.S3Result(
                bucket=os.getenv("S3_RESULT_BUCKET"),
                boto3_kwargs=dict(
                    # this should be a secret eventually
                    aws_access_key_id=os.getenv('S3_ACCESS_KEY'),
                    # this should be a secret eventually
                    aws_secret_access_key=os.getenv('S3_SECRET_KEY'),
                    endpoint_url=os.getenv('S3_URL'),
                ),
            )
            flow.register(project_name=project_name)

        logger.info("All done!")
