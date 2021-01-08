import prefect

create_task = prefect.tasks.docker.CreateContainer()
start_task = prefect.tasks.docker.StartContainer()
wait_task = prefect.tasks.docker.WaitOnContainer()
logs_task = prefect.tasks.docker.GetContainerLogs()

environment = dict(
    ftp_url="dummy-ftp",
    ftp_user="thedude",
    ftp_password="abides",
    staging_dir="/staging",
    ftp_server_dir="/reports",
    kafka_brokers="192.168.70.171,192.168.70.172,192.168.70.173",
)


with prefect.Flow("hello-flow") as flow:
    builder_container_id = create_task(
        image_name="nexus.oadomain.com:5002/ahc-report-service:latest",
        command=["poetry", "run", "builder"],
        volumes=["/staging:/staging"],
        docker_server_url="tcp://zaphod:2375",
        environment=environment,
    )
    start_task(
        container_id=builder_container_id,
        docker_server_url="tcp://zaphod:2375",
    )
    builder_exit_code = wait_task(
        container_id=builder_container_id,
        docker_server_url="tcp://zaphod:2375",
    )
    builder_logs = logs_task(
        container_id=builder_container_id,
        docker_server_url="tcp://zaphod:2375",
        upstream_tasks=[builder_exit_code],
    )
    print(builder_logs)

    uploader_container_id = create_task(
        image_name="nexus.oadomain.com:5002/ahc-report-service:latest",
        command=["poetry", "run", "uploader"],
        docker_server_url="tcp://zaphod:2375",
        volumes=["/staging:/staging"],
        upstream_tasks=[builder_exit_code],
        environment=environment,
    )
    start_task(
        container_id=uploader_container_id,
        docker_server_url="tcp://zaphod:2375",
    )
    uploader_exit_code = wait_task(
        container_id=uploader_container_id,
        docker_server_url="tcp://zaphod:2375",
    )
    uploader_logs = logs_task(
        container_id=uploader_container_id,
        docker_server_url="tcp://zaphod:2375",
        upstream_tasks=[uploader_exit_code],
    )
    print(uploader_logs)
