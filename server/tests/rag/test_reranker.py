import pytest

from server.rag.core.retrieval import Reranker


@pytest.fixture
def reranker():
    reranker = Reranker()
    return reranker


def test_rerank_empty_query(reranker):
    result = reranker("", ["text1", "text2", "text3"])
    assert isinstance(result, list)
    assert len(result) <= 3


def test_rerank_less_than_five_chunks(reranker):
    chunks = ["chunk1", "chunk2"]
    result = reranker("query", chunks)
    assert len(result) == 2
    assert all(chunk in chunks for chunk in result)


def test_rerank_returns_list(reranker):
    result = reranker("query", ["text1", "text2"])
    assert isinstance(result, list)


def test_rerank_empty_chunks(reranker):
    result = reranker("query", [])
    assert isinstance(result, list)
    assert result == []


def test_reranker_call(reranker):
    query = "third chunk"
    chunks = [
        "This is the first chunk",
        "This is the second chunk",
        "This is the third chunk",
    ]

    result = reranker(query, chunks)

    assert len(result) == 3
    assert result[0] == "This is the third chunk"


def test_rerank_limit_to_five(reranker):
    query = "Test query"
    chunks = [
        "This is the first chunk",
        "This is the second chunk",
        "This is the third chunk",
        "This is the fourth chunk",
        "This is the fifth chunk",
        "This is the sixth chunk",
    ]

    result = reranker(query, chunks)
    assert len(result) == 5
