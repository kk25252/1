# SEO 内容多智能体流水线

这是一个可运行的最小模板，用于实现你提出的完整链路：

`Research Agent -> Strategy Agent -> Outline Agent -> Writer Agent -> Editor Agent -> Fact Checker -> SEO Agent -> Publisher`

## 快速开始

```bash
python3 src/seo_content_pipeline.py "关键词示例" --audience "B2B运营" --output output
```

执行后会生成：

- `output/<keyword>.md`：文章正文（编辑后）
- `output/<keyword>.json`：策略、大纲、事实校验、SEO 元数据

## 当前实现说明

- 已内置 8 个 Agent 的串行编排与共享状态（`PipelineState`）。
- `ResearchAgent` 和 `FactCheckerAgent` 提供了接入真实数据源的 TODO 占位。
- `PublisherAgent` 已实现本地发布（写入 Markdown + JSON）。

## 推荐下一步（生产化）

1. 接入 SERP 数据供应商（SerpAPI / DataForSEO / Ahrefs）替换占位数据。
2. 用 LLM API（如 OpenAI Responses API）驱动策略、大纲、写作和润色。
3. 为事实校验增加“声明级别”校验（claim-by-claim verification）。
4. 加入质量门禁：
   - 最小字数
   - 可读性评分
   - 关键词覆盖度
   - 引用来源数量
5. 对接 CMS（WordPress / Ghost / Notion / 自建后台）实现自动发布。
