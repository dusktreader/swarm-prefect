FROM prefecthq/server:${PREFECT_SERVER_TAG:-latest}

RUN pip install loguru py-buzz
