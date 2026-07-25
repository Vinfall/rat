# Rat Ain't Tieba

RAT 是一款尊重用户自由的百度贴吧前端。

本仓库 fork 自 [rat][rat]，主要修改：

1. 使用 mise 简化安装、运行、卸载流程
2. 更新依赖以兼容 Python 3.12-3.14，并将 aioflask + Flask 替换为 Quart
3. 删除失效的图片代理功能，直接从百度获取图片[^1]，提高了可用性，但隐私层面有所减弱

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
`should_fetch_comments` 用于控制是否获取楼中楼。
如果浏览性能不佳可以考虑关闭楼中楼获取。

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

[^1]: Firefox 用户如果仍然无法访问图片，可能需要关闭 Enhanced Tracking Protection。

[rat]: https://0xacab.org/johnxina/rat
