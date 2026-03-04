from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class PipelineState:
    """Shared state passed through every agent."""

    keyword: str
    locale: str = "zh-CN"
    audience: str = "general"
    serp_data: Dict[str, Any] = field(default_factory=dict)
    strategy: Dict[str, Any] = field(default_factory=dict)
    outline: Dict[str, Any] = field(default_factory=dict)
    draft: str = ""
    edited: str = ""
    fact_check: Dict[str, Any] = field(default_factory=dict)
    seo: Dict[str, Any] = field(default_factory=dict)
    publication: Dict[str, Any] = field(default_factory=dict)


class BaseAgent:
    name = "base"

    def run(self, state: PipelineState) -> PipelineState:
        raise NotImplementedError


class ResearchAgent(BaseAgent):
    name = "research"

    def run(self, state: PipelineState) -> PipelineState:
        # TODO: Integrate SERP API provider, e.g., SerpAPI, DataForSEO.
        state.serp_data = {
            "keyword": state.keyword,
            "top_results": [
                "Result A (placeholder)",
                "Result B (placeholder)",
                "Result C (placeholder)",
            ],
            "paa": ["用户常问问题1", "用户常问问题2"],
            "related_keywords": [f"{state.keyword} 教程", f"{state.keyword} 最佳实践"],
            "fetched_at": datetime.utcnow().isoformat(),
        }
        return state


class StrategyAgent(BaseAgent):
    name = "strategy"

    def run(self, state: PipelineState) -> PipelineState:
        state.strategy = {
            "search_intent": "informational",
            "target_persona": state.audience,
            "angle": f"帮助读者快速掌握 {state.keyword}",
            "content_type": "long_form_blog",
            "primary_keyword": state.keyword,
            "secondary_keywords": state.serp_data.get("related_keywords", []),
        }
        return state


class OutlineAgent(BaseAgent):
    name = "outline"

    def run(self, state: PipelineState) -> PipelineState:
        state.outline = {
            "title": f"{state.keyword} 完整指南",
            "h2": [
                f"什么是 {state.keyword}",
                f"为什么要关注 {state.keyword}",
                "核心方法与步骤",
                "常见误区",
                "实战案例",
                "总结与行动建议",
            ],
        }
        return state


class WriterAgent(BaseAgent):
    name = "writer"

    def run(self, state: PipelineState) -> PipelineState:
        sections = "\n".join([f"## {item}\n（正文占位）" for item in state.outline.get("h2", [])])
        state.draft = f"# {state.outline.get('title', state.keyword)}\n\n{sections}\n"
        return state


class EditorAgent(BaseAgent):
    name = "editor"

    def run(self, state: PipelineState) -> PipelineState:
        state.edited = (
            state.draft
            + "\n\n---\n编辑建议：补充数据引用、加入过渡句、强化结论中的 CTA。\n"
        )
        return state


class FactCheckerAgent(BaseAgent):
    name = "fact_checker"

    def run(self, state: PipelineState) -> PipelineState:
        # TODO: Validate each factual claim against trusted sources.
        state.fact_check = {
            "status": "needs_review",
            "notes": [
                "占位稿无事实性引用，请在发布前补充权威来源。",
            ],
        }
        return state


class SEOAgent(BaseAgent):
    name = "seo"

    def run(self, state: PipelineState) -> PipelineState:
        state.seo = {
            "title_suggestion": state.outline.get("title", ""),
            "meta_description": f"这篇文章系统讲解 {state.keyword}，涵盖方法、案例与常见误区。",
            "internal_links": ["/blog/related-post-1", "/blog/related-post-2"],
            "keyword_density_hint": "1.0% - 1.8%",
        }
        return state


class PublisherAgent(BaseAgent):
    name = "publisher"

    def __init__(self, output_dir: str = "output") -> None:
        self.output_dir = Path(output_dir)

    def run(self, state: PipelineState) -> PipelineState:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        slug = state.keyword.strip().lower().replace(" ", "-")
        article_file = self.output_dir / f"{slug}.md"
        metadata_file = self.output_dir / f"{slug}.json"

        article_file.write_text(state.edited, encoding="utf-8")
        metadata_file.write_text(
            json.dumps(
                {
                    "strategy": state.strategy,
                    "outline": state.outline,
                    "fact_check": state.fact_check,
                    "seo": state.seo,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        state.publication = {
            "article_path": str(article_file),
            "metadata_path": str(metadata_file),
            "status": "published_locally",
        }
        return state


class Pipeline:
    def __init__(self, agents: List[BaseAgent]):
        self.agents = agents

    def run(self, state: PipelineState) -> PipelineState:
        for agent in self.agents:
            state = agent.run(state)
        return state


def build_default_pipeline(output_dir: str = "output") -> Pipeline:
    return Pipeline(
        agents=[
            ResearchAgent(),
            StrategyAgent(),
            OutlineAgent(),
            WriterAgent(),
            EditorAgent(),
            FactCheckerAgent(),
            SEOAgent(),
            PublisherAgent(output_dir=output_dir),
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SEO Content Agent Pipeline")
    parser.add_argument("keyword", type=str, help="Main keyword")
    parser.add_argument("--audience", type=str, default="general", help="Target audience")
    parser.add_argument("--locale", type=str, default="zh-CN", help="Locale")
    parser.add_argument("--output", type=str, default="output", help="Output directory")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    state = PipelineState(keyword=args.keyword, audience=args.audience, locale=args.locale)
    pipeline = build_default_pipeline(output_dir=args.output)
    final_state = pipeline.run(state)
    print(json.dumps(final_state.publication, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
