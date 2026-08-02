from app.search.search_engine import search


def test_search_returns_results_for_known_term(client):
    context = client.app.state.search_context
    results = search(query="space shuttle", context=context, top_k=5)
    assert len(results) > 0
    assert len(results) <= 5


def test_search_results_are_sorted_descending(client):
    context = client.app.state.search_context
    results = search(query="space shuttle", context=context, top_k=5)
    scores = [r.score for r in results]
    assert scores == sorted(scores, reverse=True)


def test_search_returns_empty_for_nonsense_query(client):
    context = client.app.state.search_context
    results = search(query="zzzznonexistenttermzzzz", context=context, top_k=5)
    assert results == []