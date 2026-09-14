FROM astral/uv:python3.10-trixie-slim
COPY pyproject.toml /tmp/pyproject.toml
RUN apt update && apt install -y sumo sumo-tools build-essential cargo time && uv pip install --system -r /tmp/pyproject.toml
