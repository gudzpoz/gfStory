# gfStory

这是一款少女前线（一）的剧情模拟器……总之预先关服撒花~

```
但就像我之前说的，生活的90%都取决于你如何对待！
但是光明的一面是什么呢？我确实不知道啦，也许你只要保持专注，它会突然落到你的身上？
祝你好运，朱莉安，还有Jo。

……也祝这个世界好运。
```

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

- 运行 `gf-resource-downloader` 下载资源（大更新的话说不定要把 `output` 给先清空一下）。

- 更新 `gf-data-ch` 目录，到目录里去 `git pull` 一下，因为剧情资源的索引是直接从这边读取的。

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

## 剧情归档

目前还有很多战斗中剧情、点位剧情没有归档，这里把目前找到的先记录下来：

- 主线：目前手动归档了 EP 0 ~ 13 的剧情。之后的包括双联乱数以及后面的都还没有处理，有一大堆。
  - 第十一战役：11-10-4-point9292.txt
- 小型活动：
  - 沙罗蚀相
  - 迷笼猜想
  - 思域迷航（全是乱的）
- 联动
  - 荣耀日
  - 梦间剧
  - 暗金潮
  - 小邪神前线

但是感觉之后也没什么动力来修 bug 和归档零碎剧情了，就这样吧。
