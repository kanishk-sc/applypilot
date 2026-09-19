import pytest

from backend.services.ai import OpenAIService, ProviderError


class BadEmbeddings:
    def create(self, **kwargs):
        raise TimeoutError("provider timed out")


class BadClient:
    embeddings = BadEmbeddings()


def test_embedding_provider_failure_is_safely_wrapped() -> None:
    service = object.__new__(OpenAIService)
    service.settings = type(
        "Settings",
        (),
        {"embedding_model": "test", "embedding_dimensions": 3},
    )()
    service.client = BadClient()

    with pytest.raises(ProviderError, match="embedding_request_failed"):
        service.embed("resume content")
