# mukaku

基于 [Playwright](https://playwright.dev/python/) 的命令行工具，用于在 `mukaku.com` 站点检索视频并提取对应资源的磁力链接（magnet）。仓库同时附带一份油猴（Tampermonkey）用户脚本，用于优化站点的页面体验。

> ⚠️ 本项目仅供学习与技术研究使用。请遵守目标网站的服务条款及当地法律法规，自行承担使用风险。

## 功能特性

- 🔍 **关键词搜索**：通过命令行输入关键词，自动打开搜索页并抓取结果列表。
- 🧲 **磁力提取**：进入选定的视频详情页，批量收集资源标题及对应的磁力链接。
- 🔗 **双重抓取**：同时解析页面 DOM 与拦截 `getVideoList` 接口响应，补全标题与详情页链接。
- 📜 **用户脚本**：`解锁不太灵.user.js` 用于解除 VIP 限制、优化搜索框、优雅折叠首页公告栏。

## 环境要求

- Python `>=3.14`（见 `.python-version`）
- [uv](https://github.com/astral-sh/uv) 包管理器（推荐）

## 安装

使用 `uv` 安装依赖并下载 Playwright 浏览器内核：

```bash
# 同步依赖（创建 .venv 并安装 playwright）
uv sync

# 安装 Playwright 所需的 Chromium 浏览器
uv run playwright install chromium
```

## 使用方法

运行主脚本：

```bash
uv run python main.py
```

交互流程：

1. 终端提示后输入**搜索关键词**。
2. 程序打开浏览器（非无头模式）执行搜索，并以 JSON 形式打印结果列表，每条包含 `index`、`title`、`link`。
3. 根据列表输入想要查看的**序号**。
4. 程序进入对应详情页，输出该资源下所有 `title` + `magnet` 的 JSON 结果。

示例输出：

```json
[
  {
    "index": 1,
    "title": "示例标题",
    "link": "https://web5.mukaku.com/mv/xxxxxx",
    "clickable": { "selector": ".video-card", "index": 0 }
  }
]
```

```json
{
  "selected": {
    "index": 1,
    "title": "示例标题",
    "link": "https://web5.mukaku.com/mv/xxxxxx"
  },
  "resources": [
    { "title": "示例资源 1080P", "magnet": "magnet:?xt=urn:btih:..." }
  ]
}
```

## 工作原理

`main.py` 的核心流程：

| 函数 | 说明 |
| --- | --- |
| `collect_search_results(page, keyword)` | 打开搜索页，监听 `getVideoList` 接口响应，并结合 `.video-card` DOM 元素生成结果列表 |
| `open_selected_result(page, item)` | 点击选中的卡片进入详情页；若点击未生效则回退为直接跳转 `link` |
| `collect_resources(page)` | 在 `.resource-items-group.modern-list` 中提取每个资源卡片的标题与磁力链接 |

关键常量：

- `BASE_URL = "https://web5.mukaku.com"`
- `SEARCH_CARD_SELECTOR = ".video-card"`
- `RESOURCE_GROUP_SELECTOR = ".resource-items-group.modern-list"`

> 说明：脚本默认以**有头模式**（`headless=False`）启动浏览器，便于观察执行过程。如需无头运行，可将 `main.py` 中 `browser = p.chromium.launch(headless=False)` 改为 `headless=True`。

## 用户脚本：解锁不太灵

`解锁不太灵.user.js` 是一份 Tampermonkey/Greasemonkey 用户脚本（v1.1，MIT 许可）：

- 解除站点的 VIP 限制
- 优化顶部搜索框样式与交互
- 将首页公告栏优雅折叠隐藏

**安装方法**：在浏览器中安装 [Tampermonkey](https://www.tampermonkey.net/) 扩展，新建脚本并粘贴该文件内容，或直接拖入安装。脚本已配置匹配 `mukaku.com`、`butai0.*`、`*bt0.com` 等多个站点域名。

## 项目结构

```
mukaku/
├── main.py              # 搜索 / 磁力提取主程序
├── 解锁不太灵.user.js    # 油猴用户脚本
├── pyproject.toml       # 项目元数据与依赖
├── uv.lock              # 依赖锁定文件
├── .python-version      # Python 版本（3.14）
└── README.md
```

## 许可证

用户脚本部分采用 MIT 许可证。
