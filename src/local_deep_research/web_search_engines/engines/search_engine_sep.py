"""Stanford Encyclopedia of Philosophy (SEP) search engine."""

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urljoin

from langchain_core.language_models import BaseLLM
from loguru import logger

from ...security.safe_requests import safe_get
from ..search_engine_base import BaseSearchEngine


class SEPSearchEngine(BaseSearchEngine):
    """Search SEP through its official public search endpoint."""

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
        self.base_url = "https://plato.stanford.edu"
        self.search_url = f"{self.base_url}/search/searcher.py"

    @staticmethod
    def _strip_html(text: str) -> str:
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _get_previews(self, query: str) -> List[Dict[str, Any]]:
        self._last_wait_time = self.rate_tracker.apply_rate_limit(self.engine_type)
        params = {"query": query}
        response = safe_get(self.search_url, params=params, timeout=30)
        response.raise_for_status()

        html = response.text
        pattern = re.compile(
            r'<a[^>]+href="(?P<href>/entries/[^"]+)"[^>]*>(?P<title>.*?)</a>(?P<rest>.*?)(?=<a[^>]+href="/entries/|$)',
            re.IGNORECASE | re.DOTALL,
        )

        previews: list[dict[str, Any]] = []
        seen: set[str] = set()
        for match in pattern.finditer(html):
            href = match.group("href")
            if href in seen:
                continue
            seen.add(href)

            title = self._strip_html(match.group("title"))
            rest = self._strip_html(match.group("rest"))
            snippet = rest[:400] if rest else ""
            previews.append(
                {
                    "id": href,
                    "title": title,
                    "link": urljoin(self.base_url, href),
                    "snippet": snippet,
                    "source": "SEP",
                    "query_url": f"{self.search_url}?{urlencode(params)}",
                }
            )
            if len(previews) >= self.max_results:
                break

        logger.info(f"SEP returned {len(previews)} preview results")
        return previews
