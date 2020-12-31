import prefect

pull_task = prefect.tasks.docker.PullImage()
create_task = prefect.tasks.docker.CreateContainer()
start_task = prefect.tasks.docker.StartContainer()
status_task = prefect.tasks.docker.WaitOnContainer()


with prefect.Flow("hello-flow") as flow:
    pulled = pull_task(
        repository="python",
        tag="3.9-slim",
    )
    container_id = create_task(
        image_name="python:3.9-slim",
        command='python -c "print "Hello Universe!"',
        upstream_tasks=[pulled],
    )
    start_task(container_id=container_id)
    exit_code = status_task(container_id=container_id)

# flow.storage = prefect.storage.Docker(image_name='hello-docker', image_tag='latest')
# flow.storage.build()
flow.run_config = prefect.run_configs.DockerRun(
    image="python:3.9-slim",
)