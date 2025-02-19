# THU-eReserves-Crawler

从清华大学电子教学参考书服务平台爬取指定的电子教参，将指定页码范围内的页面以 jpg 格式保存到本地。

## 使用说明

### 1. 配置 `config.json` 文件

登录[清华大学电子教学参考书服务平台](https://ereserves.lib.tsinghua.edu.cn/)，进入需要爬取的书籍主页。

按 `F12` 打开开发者工具，切换到 “网络” 标签页并刷新页面。

找到 `access` 请求，将请求标头中的 `Jcclient` 字段复制到 `config.json` 文件的对应位置。

再将 `Referer` 字段中 `bookDetail/` 之后的编号复制到 `config.json` 中的 `bookId` 中。

![bookDetail](/img/bookDetail.jpg)

点击 “立即阅读” ，`F12` 打开开发者工具，切换到 “网络” 标签页并刷新页面。

找到 `selectJgpBookChapters` 请求，将请求标头中的 `Botureadkernel` 字段复制到 `config.json` 文件的对应位置。

![Botureadkernel](/img/readKernel.jpg)

`config.json` 中的 `start` 项设置为起始页码（含）； `end` 项设置为终止页码（含），若到最后一页终止可设置为 `-1` 。

### 2. 运行脚本

确保安装所有依赖后运行脚本。

```
python THU-eReserves-Crawler.py
```

脚本会自动爬取该书籍的每一页，并以 jpg 格式保存到当前目录下的 `{title}` 文件夹中。原书名中含有的非法文件名字符，会在保存路径中被替换为 `.` 。

### 3. 附加说明

爬取的 jpg 文件可通过 PDF 编辑器一次性合并得到 PDF 版教参。

创建此脚本仅为方便阅读教参，所下载的内容**仅限个人阅读**。

## LISENCE

本仓库的内容采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可协议。您可以自由使用、修改、分发和创作衍生作品，但只能用于非商业目的，并署名原作者，以相同的授权协议共享衍生作品。

如果您认为文档的部分内容侵犯了您的合法权益，请联系项目维护者，我们会尽快删除相关内容。
