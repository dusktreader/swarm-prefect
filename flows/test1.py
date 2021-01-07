import prefect

create_task = prefect.tasks.docker.CreateContainer()
start_task = prefect.tasks.docker.StartContainer()
status_task = prefect.tasks.docker.WaitOnContainer()


with prefect.Flow("hello-flow") as flow:
    container_id = create_task(
        image_name="python:3.9-slim",
        command='python -c "print \"Hello Universe!\""',
        docker_server_url="tcp://zaphod:2375",
    )
    start_task(container_id=container_id)
    exit_code = status_task(container_id=container_id)
