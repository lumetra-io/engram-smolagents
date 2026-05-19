"""
engram_smolagents — durable memory tools for HuggingFace smolagents.

smolagents wraps tools with the @tool decorator. This module returns a list
of `Tool` instances bound to a single Engram bucket that any smolagent can
plug into.

Usage:

    from smolagents import CodeAgent
    from engram_smolagents import engram_tools

    agent = CodeAgent(
        tools=engram_tools(bucket="my-agent"),
        model=...,
    )
"""

from __future__ import annotations

import os
from typing import List, Optional

from smolagents import Tool
from lumetra_engram import EngramClient


def engram_tools(
    bucket: str,
    *,
    client: Optional[EngramClient] = None,
) -> List[Tool]:
    """Return smolagents Tool instances bound to a single Engram bucket."""
    c = client or EngramClient(api_key=os.environ.get("ENGRAM_API_KEY"))

    class StoreMemory(Tool):
        name = "engram_store_memory"
        description = (
            "Save an atomic fact (one concept) to durable memory. Use for "
            "user preferences, decisions, observations worth remembering "
            "across sessions."
        )
        inputs = {"content": {"type": "string", "description": "Fact to remember."}}
        output_type = "string"

        def forward(self, content: str) -> str:
            r = c.store_memory(content, bucket)
            return f"stored {r.get('memory_id', '(unknown)')}"

    class QueryMemory(Tool):
        name = "engram_query_memory"
        description = (
            "Hybrid retrieval + synthesized answer over stored memories. "
            "Use before answering questions about prior context."
        )
        inputs = {"question": {"type": "string", "description": "Natural-language question."}}
        output_type = "string"

        def forward(self, question: str) -> str:
            r = c.query(question, buckets=[bucket])
            ans = r.get("answer") or ""
            return ans.split("FINAL ANSWER:")[-1].strip() or "No memories found."

    return [StoreMemory(), QueryMemory()]
