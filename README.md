# Rat Aint Tieba

RAT 是一款尊重用户自由的百度贴吧前端。RAT 项目内所有文件均以 AGPLv3 分发，具体内容
见 LICENSE。

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

## 运行

调试运行（已知在生产环境有内存溢出）：

```sh
mise run debug
```

生产环境运行：

```sh
mise run serve
```

默认参数下，你应将反向代理指向 `127.0.0.1:8000`。

## 配置

其中的 `should_fetch_comments` 用于控制是否获取楼中楼。如果浏览性能不佳可以考虑
关闭楼中楼获取。
