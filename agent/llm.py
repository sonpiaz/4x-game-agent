"""
LLM Vision API — Send screenshots to vision-capable LLMs and get structured responses.

Supports Claude (Anthropic) out of the box.
Game-specific prompts belong in each game's module — this is just the API wrapper.
"""
import json


class LLMVision:
    """Send images to a vision LLM and parse JSON responses."""

    def __init__(self, provider: str = "anthropic", api_key: str = None):
        self.provider = provider
        if provider == "anthropic":
            import anthropic
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        self.call_count = 0

    def ask(self, screenshot_b64: str, prompt: str,
            model: str = "claude-sonnet-4-20250514",
            max_tokens: int = 1500) -> dict:
        """Send a screenshot + prompt to the LLM. Returns parsed JSON dict.

        Args:
            screenshot_b64: Base64-encoded JPEG screenshot.
            prompt: Text prompt (should request JSON output).
            model: Model ID to use.
            max_tokens: Max response tokens.

        Returns:
            Parsed JSON dict from the LLM response, or a fallback dict
            with action="wait" on parse failure.
        """
        self.call_count += 1

        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image", "source": {
                            "type": "base64", "media_type": "image/jpeg",
                            "data": screenshot_b64,
                        }},
                        {"type": "text", "text": prompt},
                    ],
                }],
            )
            raw = response.content[0].text.strip()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        return self._parse_json(raw)

    @staticmethod
    def _parse_json(raw: str) -> dict:
        """Parse JSON from LLM response, handling markdown code blocks."""
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(raw[start:end])
                except json.JSONDecodeError:
                    pass
            return {
                "action": "wait",
                "target": "parse_error",
                "reason": f"Failed to parse: {raw[:200]}",
            }
