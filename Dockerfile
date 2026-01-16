ARG IFLOW_CLI_VERSION=0.5.1
FROM ghcr.io/timandes/iflow-cli-sdk-python-image:${IFLOW_CLI_VERSION}

WORKDIR /app

COPY . .

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    export PATH="$HOME/.local/bin:$PATH" && \
    uv sync --frozen

RUN groupadd -r iflow && useradd -r -g iflow iflow
USER iflow:iflow


