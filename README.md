# Rat Ain't Tieba

RAT 是一款尊重用户自由的百度贴吧前端。

本仓库 fork 自 [johnxina/rat][rat]，主要修改：

1. 使用 mise 简化安装、运行、卸载流程，并提供 SystemD 服务
2. 更新依赖以兼容 Python 3.12-3.14，并将 aioflask + Flask 替换为 Quart
3. 删除失效的图片代理功能，直接从百度获取图片[^1]
4. 修复楼中楼回复排序
5. 移除百度外链跳转，直接展示原始链接

## 安装

```sh
# 参考文档安装 mise
# https://mise.jdx.dev/getting-started.html#installing-mise-cli
# 信任 mise 配置
mise trust
# 安装命令行依赖
mise install
# 安装 Python 依赖
mise run install
```

## 配置

见 [shared.py](shared.py)。

SystemD 示例见 [rat.service](rat.service)，需要修改为实际用户名和路径。

## 运行

调试运行：

```sh
mise run debug
```

生产环境运行：

```sh
mise run serve
```

默认参数下，你应将反向代理指向 `127.0.0.1:8000`。

如果出于某些原因（e.g. 纯内网部署）希望绑定到 `0.0.0.0:8000`，可以修改 [.mise.toml](.mise.toml) 的 serve task 运行参数：

```diff
[tasks.serve]
description = "run prod server"
run = """
#!/usr/bin/env bash
source .venv/bin/activate
-gunicorn app:app --max-requests 50 --workers 2 --worker-class uvicorn.workers.UvicornWorker
+gunicorn app:app --max-requests 50 --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
"""
```

## 卸载

```sh
# 删除虚拟环境
rm -rf .venv
# 删除 Python 软件包缓存
uv cache prune
# 卸载 mise
# 手动删除见 https://mise.jdx.dev/installing-mise.html#uninstalling
mise implode
# 删除本项目
cd ..
rm -rf rat
```

## 许可

RAT 项目内所有文件均以 AGPLv3 分发，具体内容见 [LICENSE](LICENSE)。

[^1]: Firefox 用户如果仍然无法访问图片，可能需要关闭 Enhanced Tracking Protection。如果希望减少请求，可以在 [share.py](shared.py) 禁用用户头像和等级。

[rat]: https://0xacab.org/johnxina/rat
