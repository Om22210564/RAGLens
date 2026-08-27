import json
import re
from dataclasses import dataclass
from typing import Any, Protocol

from app.core.config import Settings
from app.generation.context import ContextItem, render_untrusted_context
from app.generation.prompts import GROUNDED_SYSTEM_PROMPT


@dataclass(frozen=True, slots=True)
class GenerationResult:
    answer: str
    cited_ids: tuple[int, ...]  # The answer cites chunks


class LLMProvider(Protocol):
    async def generate(self, query: str, context: list[ContextItem]) -> GenerationResult: ...


class GenerationProviderError(RuntimeError):
    """A remote generation provider failed without exposing its details to clients."""


# Any LLM provider in this application must provide a generate() method like this.


class ExtractiveGroundedProvider:
    """No-network baseline; replace with an LLM provider through this interface."""

    async def generate(self, query: str, context: list[ContextItem]) -> GenerationResult:
        # The first context item is the highest-ranked evidence for this baseline.
        first = context[0]
        excerpt = first.chunk.text.strip().replace("\n", " ")
        if len(excerpt) > 600:
            excerpt = excerpt[:597].rsplit(" ", maxsplit=1)[0] + "..."
        return GenerationResult(
            answer=f"Based on the available evidence: {excerpt} [{first.citation_id}]",
            cited_ids=(first.citation_id,),
        )


class GroqLLMProvider:
    """Groq chat-completions adapter with local citation-ID validation."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model
        self._client: Any | None = None

    async def generate(self, query: str, context: list[ContextItem]) -> GenerationResult:
        client = self._get_client()
        try:
            completion = await client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": GROUNDED_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"USER QUERY:\n{query}\n\n{render_untrusted_context(context)}\n\n"
                            'Return JSON only: {"answer": string, "citations": [integer]}. '
                            "Citations must be supplied source IDs."
                        ),
                    },
                ],
            )
        except Exception as exc:
            raise GenerationProviderError("Generation provider request failed") from exc
        raw = completion.choices[0].message.content or "{}"
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"answer": raw, "citations": re.findall(r"\[(\d+)\]", raw)}
        allowed = {item.citation_id for item in context}
        citations = tuple(
            citation
            for value in payload.get("citations", [])
            if isinstance(value, int) and (citation := value) in allowed
        )
        return GenerationResult(answer=str(payload.get("answer", "")).strip(), cited_ids=citations)

    def _get_client(self) -> Any:
        if self._client is None:
            from groq import AsyncGroq

            self._client = AsyncGroq(api_key=self.api_key)
        return self._client


def create_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "groq":
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is required when APP_LLM_PROVIDER=groq")
        return GroqLLMProvider(settings.groq_api_key, settings.groq_model)
    if settings.llm_provider == "extractive":
        return ExtractiveGroundedProvider()
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
