# engram-smolagents

[smolagents](https://github.com/huggingface/smolagents) integration for [Engram](https://lumetra.io) — durable memory tools for HuggingFace's lightweight agent framework.

Returns two smolagents `Tool` instances (`engram_store_memory`, `engram_query_memory`) bound to a single Engram bucket. Plug them into any `CodeAgent` or `ToolCallingAgent` and the agent gains persistent cross-session memory with hybrid retrieval.

## Install

```bash
pip install lumetra-engram smolagents
```

Vendor `engram_smolagents.py` from this repo (~50 LOC). PyPI release coming.

```bash
export ENGRAM_API_KEY="eng_live_..."
```

## Get an Engram API key

Sign up at <https://lumetra.io> — free tier, no card. You'll see an `eng_live_…` token in your dashboard.

**Don't forget BYOK** — Engram is bring-your-own-key end-to-end for the LLM that does extraction + synthesis. Configure a provider at <https://lumetra.io/models>. DeepSeek is what we recommend. Without one, store/query returns HTTP 412.

## Usage

```python
from smolagents import CodeAgent, LiteLLMModel
from engram_smolagents import engram_tools

agent = CodeAgent(
    tools=engram_tools(bucket="my-agent"),
    model=LiteLLMModel(model_id="deepseek/deepseek-chat"),
)

agent.run("Remember that I prefer dark mode and use vim for everything.")
# Later, in a fresh process:
agent.run("What were my UI preferences?")
```

The agent's tool palette now includes:

- `engram_store_memory(content)` — save an atomic fact.
- `engram_query_memory(question)` — hybrid retrieval + synthesized answer.

## Why this beats in-process memory

- **Persists across `agent.run()` calls.** smolagents resets per run; Engram doesn't.
- **Hybrid retrieval** — BM25 + vector + knowledge graph fusion.
- **Bring-your-own-LLM** for extraction and synthesis (<https://lumetra.io/models>).
- **Per-agent / per-user buckets** — pass `bucket=f"user-{user_id}"` and isolation is automatic.

## Verified

Smoke-tested against live `api.lumetra.io`:

- `store_memory.forward("smolagents uses 'forward' instead of '_run' for tool invocation.")` → stored.
- `store_memory.forward("smolagents tools subclass smolagents.Tool and override forward(...).")` → stored.
- `query_memory.forward("Which method does a smolagents Tool override for invocation?")` → answer: `"forward()."`

## License

MIT — Lumetra
