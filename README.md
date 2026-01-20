# iFlow CLI Ralph Loop

这个项目旨在通过IFlow CLI复现原始的Claude Code的插件[Ralph Loop](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/ralph-loop)的能力。

## 命令行参数

- `--max-iterations`: 最大迭代次数（默认：10）
- `--completion-promise`: 完成关键词（默认：ALL-DONE）
- `--work-dir`: iflow 工作目录（默认：当前目录）

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

## 使用示例

1）进入工作目录

```bash
cd /path/to/work
```

2）修改当前目录的权限

```bash
chmod 777 .
```

3）创建PROMPTS.txt

```bash
echo 'xxxx' > PROMPTS.txt
```

注意追加完成提示词：

```bash
echo '结束时输出<promise>COMPLETE</promise>' >> PROMPTS.txt
```

4）开始工作

```bash
cat PROMPTS.txt | docker run --rm -i \
  -e IFLOW_SELECTED_AUTH_TYPE=iflow \
  -e IFLOW_BASE_URL=https://apis.iflow.cn/v1 \
  -e IFLOW_MODEL_NAME=glm-4.7 \
  -e IFLOW_API_KEY=sk-xxxxxx \
  -v `pwd`:/workdir \
  ghcr.io/timandes/iflow-cli-ralph-loop:0.5.1 \
  uv run -m main --max-iterations 5 --completion-promise "COMPLETE" --work-dir /workdir
```
