from unittest.mock import MagicMock, patch

from src.local_deep_research.web_search_engines.engines.search_engine_sep import (
    SEPSearchEngine,
)


@patch("src.local_deep_research.web_search_engines.engines.search_engine_sep.safe_get")
def test_sep_parses_results(mock_get):
    response = MagicMock()
    response.text = '<a href="/entries/ethics/">Ethics</a><p>Author: A. Smith</p>'
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    engine = SEPSearchEngine(max_results=5)
    results = engine._get_previews("ethics")

    assert len(results) == 1
    assert results[0]["title"] == "Ethics"
    assert results[0]["link"] == "https://plato.stanford.edu/entries/ethics/"
    assert results[0]["source"] == "SEP"


@patch("src.local_deep_research.web_search_engines.engines.search_engine_sep.safe_get")
def test_sep_empty_results(mock_get):
    response = MagicMock()
    response.text = "<html><body>No results</body></html>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    engine = SEPSearchEngine(max_results=5)
    assert engine._get_previews("nohit") == []
