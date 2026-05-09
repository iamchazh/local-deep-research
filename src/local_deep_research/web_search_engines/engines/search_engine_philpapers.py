"""PhilPapers search engine implementation."""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

from langchain_core.language_models import BaseLLM
from loguru import logger

from ...security.safe_requests import safe_get
from ..search_engine_base import BaseSearchEngine


class PhilPapersSearchEngine(BaseSearchEngine):
    """Search PhilPapers using the public web search endpoint."""

    is_public = True
    is_scientific = True
    is_lexical = True
    needs_llm_relevance_filter = True

    def __init__(
        self,
        max_results: int = 10,
        llm: Optional[BaseLLM] = None,
        max_filtered_results: Optional[int] = None,
        settings_snapshot: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(
            llm=llm,
            max_filtered_results=max_filtered_results,
            max_results=max_results,
            settings_snapshot=settings_snapshot,
            **kwargs,
        )
        self.base_url = "https://philpapers.org"
        self.search_url = f"{self.base_url}/s"

    @staticmethod
    def _strip_html(text: str) -> str:
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _get_previews(self, query: str) -> List[Dict[str, Any]]:
        self._last_wait_time = self.rate_tracker.apply_rate_limit(self.engine_type)
        params = {"q": query}
        response = safe_get(self.search_url, params=params, timeout=30)
        response.raise_for_status()

        html = response.text
        pattern = re.compile(
            r'<li[^>]*class="[^"]*entry[^"]*"[^>]*>(?P<item>.*?)</li>',
            re.IGNORECASE | re.DOTALL,
        )
        link_pattern = re.compile(r'<a[^>]+href="(?P<href>/rec/[^"]+)"[^>]*>(?P<title>.*?)</a>', re.IGNORECASE | re.DOTALL)

        previews: list[dict[str, Any]] = []
        for item_match in pattern.finditer(html):
            item_html = item_match.group("item")
            link_match = link_pattern.search(item_html)
            if not link_match:
                continue

            href = link_match.group("href")
            title = self._strip_html(link_match.group("title"))
            text = self._strip_html(item_html)

            previews.append(
                {
                    "id": href,
                    "title": title,
                    "link": f"{self.base_url}{href}",
                    "snippet": text[:500],
                    "source": "philpapers",
                    "authors": [],
                    "query_url": f"{self.search_url}?{urlencode(params)}",
                    "raw_source_metadata": {"provider": "philpapers", "html_excerpt": text[:800]},
                }
            )
            if len(previews) >= self.max_results:
                break

        logger.info(f"PhilPapers returned {len(previews)} preview results")
        return previews
