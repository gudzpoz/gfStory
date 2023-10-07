# gfStory

我也不知道这是什么……

## 开发说明

我觉得不会有人 fork 也不会有 PR，总之这是给我自己的笔记。

这个项目大概分为两部分，一部分是各种网页界面，另一部分是自动解包。
开发的时候需要把各种资源解包了网页界面才能运行得了。

### 解包方法

`unpack/` 目录下方的是解包脚本，依赖 [gf-resource-downloader](https://github.com/gf-data-tools/gf-resource-downloader)
来下载资源。
具体命令可以看 [`build.yml`](./.github/workflows/build.yml) 里面的。基本步骤是：

- 用 `pdm` 和 `pip` 把脚本和 `gf-resource-downloader` 的 Python 依赖弄好，
  另外把 `ffmpeg`（用于音频编码）, `pngquant`（压缩图像）, `vgmstream-cli`（解包音频）这几个程序安装好。

- 运行 `gf-resource-downloader` 下载资源。

- 运行 `gfunpack` 解包资源并生成对应的索引 JSON 文件（详见 [`build.yml`](./.github/workflows/build.yml)）。

- 把 JSON 文件拷贝到 `src/assets/` 目录下，把 `audio/` 和 `images/` 资源拷贝/移动/软链接到 `public/` 目录下。

### 开发命令

上面资源的工作做好后，如果没有 `pnpm install` 的先安装 node 的依赖，然后直接 `pnpm dev` 即可。

`pnpm dev` 命令会自动把 `viewer.html` 的入口打包成单个 HTML 文件，以便用于整体打包剧情。

### 网页构架

框架用的是 Vue，目前有三个入口点：

- `index.html`: 编辑器入口
- `simulator.html`: 剧情模拟器入口
- `viewer.html`: 剧情阅读器入口（打包用）

剧情编辑器想要提供导出成能网页直接查看的游戏成品，这里用到了打包好的 `viewer.html`（打包成了一个网页文件），
`index.html` 导出的时候做的就是把编译好的剧情直接放到 `viewer.html` 里面去。
