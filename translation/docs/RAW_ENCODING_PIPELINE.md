# 活动汉化构建：原始双字节码表

## 当前范围

活动码表为 `font_encoding.hex.json`（字符 → 十六进制字节），容量以 `font_capacity_status.generated.json` 的当前生成结果为准。保留所有原日文字形及已分配码位。当前 100 个新增字码已在 Citra 难度说明的四页测试中通过；不代表所有候选码位、字体场景、更新/DLC 或实机均验证。

旧 `font_encoding.generated.json` 为历史 CP932 代理字符码表，不再用于正式构建。运行 `plan_font.py` 无参数现在转入活动规划器；旧选项报错，避免误恢复旧容量状态。

## 安全检查

- `plan_production_font.py` 以已验证试验码表为初始种子，后续只追加，不重新排列；拒绝碰撞、非法字节和容量超出。F0–FF 首字节始终保留给控制指令。
- `build_draft_messages.py` 从原始 BMD 读取每页和角色名原始字节，只替换已选译文。未译部分不经过 CP932 再编码，直接保留。向 .NET 助手提供明确字节，避开 CP932 别名和未定义码位替换。
- `bmd_bytes.py` 独立读取 BIN/ARC/BVP/BF 中的 BMD，构建后逐消息比较字节、ID、类型、角色索引及名称。校验不依赖无法表示新字码的 Unicode 导出文本。
- 表格按同一原始字节码表写入、反解，并检查定长容量及所有非文本字节不变。
- 六套字体追加字形，回读 CMAP 一致，原字形像素保留。消息、表格、字体和组装报告绑定同一份码表 SHA-256，拒绝混用不同版本。
- 本体与 DLC 采用 `-mode=FILENAME -forcecompress` 打包，并逐文件回读比对。失败的无压缩试验包仅作证据保留，不能部署。

## 重现命令

从工作区根目录执行，任一步失败即停止后续构建：

若修改了 `translation/scene_bundles`，先执行 `python PQ1_JPN/compile_scene_bundle.py`，再执行下列第 1、2 步。更新跨路线复用时，在第 2 步后执行 `python PQ1_JPN/reuse_parallel_story.py` 审查生成的证据，确认后以 `--apply` 生成批次，再重跑第 2 步及 `python -m unittest discover -s PQ1_JPN -p test_parallel_reuse.py`，之后才进行字体规划与构建。

1. `python PQ1_JPN/compile_story_drafts.py`
2. `python PQ1_JPN/compile_translation.py`
3. `python PQ1_JPN/plan_production_font.py`
4. `python PQ1_JPN/test_raw_font.py`
5. `python PQ1_JPN/test_bmd_bytes.py`
6. `python PQ1_JPN/test_repack_bvp_text.py`
7. `python PQ1_JPN/build_draft_messages.py base`
8. 分别以 `0005`、`0006`、`0007`、`0008`、`0009` 为参数运行 `build_draft_messages.py`
9. `python PQ1_JPN/build_additive_fonts.py`
10. `python PQ1_JPN/build_draft_tables.py`
11. `python PQ1_JPN/assemble_draft_payload.py`
12. `python PQ1_JPN/pack_base_draft.py`
13. 分别以五组 DLC 编号运行 `pack_dlc_draft.py`
14. `python PQ1_JPN/verify_integrated_set.py`
15. `python PQ1_JPN/report_story_progress.py`

本体新工作包位于 `full_work/base_cpk_raw/data.cpk`，DLC 包位于 `full_work/dlc_cpk_raw/`。打包脚本不会部署 Citra，不会改原 ROM、CIA、存档；当前已安装的旧补丁保持不变。只有最终 verify_integrated_set 成功，packaged_set 的计数才代表本轮已打包结果。

## 仍需完成

剧情/界面等剩余翻译，图像文字，排版校对，全量用字持续容量检查，更新与 DLC 安装/加载验证及更广泛运行测试。DLC CPK 构建完成不等于 DLC CIA 已重建或安装。
