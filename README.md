# 「就不好好说话！」缩写工具

灵感来自[「能不能好好说话？」 拼音首字母缩写翻译工具](https://github.com/itorr/nbnhhsh)。

## 用法

请先进行构建。

启动交互式命令行界面：

```sh
$ python3 jbhhsh_cli.py
```

## 构建

需要 `python>=3.6`。

安装依赖：

```sh
$ python3 -m pip install -r requirements.txt
```

爬取[「能不能好好说话？」 拼音首字母缩写翻译工具](https://github.com/itorr/nbnhhsh)的数据库：

```sh
$ python3 download_nbnhhsh_db.py
```

爬取的数据库位于 `build/nbnhhsh.db`。

生成「就不好好说话！」数据库：

```sh
$ python3 generate_jbhhsh_db.py
```

生成的数据库位于 `build/jbhhsh.db`。

## 版权

版权所有 © NKID00 2021

使用 MIT License 进行许可。
