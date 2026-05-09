from unittest.mock import MagicMock, patch

from src.local_deep_research.web_search_engines.engines.search_engine_philpapers import (
    PhilPapersSearchEngine,
)


@patch("src.local_deep_research.web_search_engines.engines.search_engine_philpapers.safe_get")
def test_philpapers_parses_results(mock_get):
    response = MagicMock()
    response.text = '<li class="entry"><a href="/rec/SMIABC">A Paper</a><div>Jane Doe</div></li>'
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    engine = PhilPapersSearchEngine(max_results=5)
    results = engine._get_previews("paper")

    assert len(results) == 1
    assert results[0]["title"] == "A Paper"
    assert results[0]["link"] == "https://philpapers.org/rec/SMIABC"
    assert results[0]["source"] == "philpapers"
    assert results[0]["raw_source_metadata"]["provider"] == "philpapers"


@patch("src.local_deep_research.web_search_engines.engines.search_engine_philpapers.safe_get")
def test_philpapers_empty_results(mock_get):
    response = MagicMock()
    response.text = "<html><body>No results</body></html>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    engine = PhilPapersSearchEngine(max_results=5)
    assert engine._get_previews("nothing") == []
