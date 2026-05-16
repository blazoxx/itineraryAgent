import pytest
import asyncio

import services.llm_service as llm


@pytest.mark.asyncio
async def test_llm_service_retries(monkeypatch):
    calls = {"count": 0}

    class FakeResp:
        def __init__(self, text):
            self.text = text

    def flaky_generate_content(model, contents):
        # fail once then succeed
        if calls["count"] == 0:
            calls["count"] += 1
            raise Exception("transient error")
        return FakeResp("ok")

    # patch the underlying client models.generate_content
    monkeypatch.setattr(llm.client.models, "generate_content", flaky_generate_content)

    res = await llm.ask_llm("hello")

    assert res == "ok"
    assert calls["count"] == 1
