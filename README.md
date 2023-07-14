# Rat Aint Tieba

RAT 是一款尊重用户自由的百度贴吧前端。RAT 项目内所有文件均以 AGPLv3 分发，具体内容
见 LICENSE。

## 部署方法

```
$ cd rat
$ virtualenv venv
$ . venv/bin/activate
(venv) $ pip install -r requirements.txt
(venv) $ patch -p1 < aiotieba-handle-exception-expose.patch
```

若 `patch` 命令提示需要文件路径，输入对应路径即可。

## 运行方法

```
(venv) $ python main.py
```

默认配置下，你应将反向代理指向 `127.0.0.1:8885`。

## 配置方法

打开 `shared.py` 修改 `app.config['SERVER_NAME']` 中冒号后的数字来改变端口号。
因为 twisted 的原因，你需要将代理指向那个端口号 -1 的端口上。

其中的 `should_fetch_comments` 用于控制是否获取楼中楼。如果浏览性能不佳可以考虑
关闭楼中楼获取。
