# 开源文件包使用说明

本地完善版：2026-10-27；未上传 GitHub。作者、正式项目名称、仓库地址、DOI、代码及数据许可证均待确定。

## 如何选择文件包

1. 需要模型、网格和数据：下载 main.zip。
2. 只需审阅数据、图片和复算统计：下载 source.zip；不含网格与场文件。
3. 需要逐时刻重新提取截面或流场：另选 checkpoint_assets 中相应网格的检查点包。11 个 ZIP 都可单独解压，不是必须凑齐才能打开的分卷。

将 main.zip 和选中的检查点 ZIP 解压至同一父目录，形成一个 fluent-pipe-reproducibility 文件夹即可。main 和 source 二选一；不必重复解压两者。

## 本版补全内容

- 三网格、150 s 共同起点、160 s 末场以及各 40 组中间 case/data 对。
- 前期已保存的监测历史（33.55–149.54 s），以及包含150 s参考点的整理表和150 s纵向剖面。
- 三网格每步末残差、原始迭代残差及已脱敏文字日志。
- 粗网格独立密集监测续算的200个真实记录点；它与三网格粗网格40点试验分别存放。
- 时间步、出口边界、糙率解析计算数据，以及对应末场和已提供图片。
- 源文件校验值、字段字典、来源索引、论文图表对应表和可执行统计脚本。

## 先看哪些文件

metadata/figure_table_map.csv 按论文顺序连接图片、表格和CSV；summary/ 给出复算结果。原有Excel按原样保存，便于阅读和追溯。图3-3应采用 data/time_step/exact_section_corrected.csv 的修正口径，不能直接沿用旧Excel中的时间步水深列。

## 本机检查命令

在解压目录打开终端执行：

```sh
python scripts/verify_and_summarize.py --verify-files
```

不加 --verify-files 只核对数据点数、时间窗口、差值公式并重算统计。脚本不启动Fluent。原生模型复算另见 REPRODUCE.md。

## 发布前填写

作者与贡献、项目名、仓库URL、许可证和模型数据的分享权利。填写后再将CITATION.cff.template改为正式CITATION.cff。发布步骤见 PUBLISH_TO_GITHUB.md。
