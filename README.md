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

调试运行（已知在生产环境下有内存溢出）：

```
(venv) $ python main.py
```

生产环境运行：

```
(venv) $ gunicorn app:proxified --max-requests 50 --workers 2 --worker-class uvicorn.workers.UvicornWorker
```

默认参数下，你应将反向代理指向 `127.0.0.1:8000`。

## 配置方法

其中的 `should_fetch_comments` 用于控制是否获取楼中楼。如果浏览性能不佳可以考虑
关闭楼中楼获取。
