# 使用指南

本仓库在加载 `esphome` 包时会自动应用 Github 链接重写补丁，
将所有指向 `github.com` 的 URL 改写为指定镜像前缀。

## 环境要求
- Python 3.12 及以上
- 安装依赖：`pip install -r requirements.txt` 和 `pip install dowhen`

## 设置镜像
默认镜像地址为 `https://gh.161024.xyz`。
如需自定义，设置环境变量 `CUSTOM_GITHUB_URL`：

```bash
export CUSTOM_GITHUB_URL="https://mirror.example.com"
```

## 使用方法
在任何脚本中导入本项目即可自动生效，或直接使用命令行工具 `esphome-cn`：

```python
import esphome

```

运行示例：

```bash
esphome-cn run livingroom.yaml
```

此后无论是 `requests` 还是 `git` 操作，只要包含 `github.com` 都会被重写到镜像地址。
