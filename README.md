# iFlow CLI Ralph Loop

## Docker Usage

### Interactive Mode

```bash
docker run --rm -it \
  -e IFLOW_SELECTED_AUTH_TYPE=iflow \
  -e IFLOW_BASE_URL=https://apis.iflow.cn/v1 \
  -e IFLOW_MODEL_NAME=glm-4.7 \
  -e IFLOW_API_KEY=sk-xxxxxx \
  ghcr.io/timandes/iflow-cli-ralph-loop:0.5.1 \
  uv run -m main
```

### Pipe Input Mode

```bash
cat PROMPTS.txt | docker run --rm -i \
  -e IFLOW_SELECTED_AUTH_TYPE=iflow \
  -e IFLOW_BASE_URL=https://apis.iflow.cn/v1 \
  -e IFLOW_MODEL_NAME=glm-4.7 \
  -e IFLOW_API_KEY=sk-xxxxxx \
  ghcr.io/timandes/iflow-cli-ralph-loop:0.5.1 \
  uv run -m main
```