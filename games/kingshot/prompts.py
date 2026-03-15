import anthropic
import json
import config
from brain.strategy import STRATEGY_KNOWLEDGE, GameStateMemory

# ─── STRATEGIC PROMPT (Sonnet, every ~60s) ───────────────────────
# Decides WHAT to do. Returns a goal + assessment.
STRATEGIC_PROMPT = """You are the strategic brain of a Kingshot game bot.
{strategy_knowledge}

{strategic_context}

Analyze this screenshot. Decide the SINGLE most important goal right now.

Return ONLY valid JSON:
{{
  "screen": "what screen we're on",
  "power_visible": number or null,
  "tc_level_visible": number or null,
  "gems_visible": number or null,
  "builders_idle": true/false/null,
  "research_idle": true/false/null,
  "training_idle": true/false/null,
  "goal": "short goal name (e.g. upgrade_range, train_troops, start_research)",
  "goal_description": "1-2 sentences: what to achieve and why",
  "first_step": "the very first tap or action to take toward this goal"
}}
"""

# ─── TACTICAL PROMPT (Haiku, every ~3s) ──────────────────────────
# Decides WHERE to tap. Returns exactly ONE action.
TACTICAL_PROMPT = """You control a Kingshot game bot. Look at this screenshot.

CURRENT GOAL: {goal}
GOAL DETAILS: {goal_description}
STEPS SO FAR: {steps_taken}
LAST ACTION: {last_action}
LAST RESULT: {last_result}

The image is {img_w}x{img_h} pixels. Return coordinates ON THIS IMAGE.

CRITICAL RULES:
- NEVER use "back" action — it triggers a QUIT GAME dialog in Kingshot!
  Instead, tap the X/close button visible on popups.
- If you see a "quit game" or "exit" confirmation dialog, tap CANCEL on it.
- If stuck on a popup after 3+ attempts, try "done" and let the strategic brain re-plan.
- Be precise with coordinates — tap the CENTER of buttons, not edges.
- Bottom navigation tabs are at the very bottom of screen (y ≈ {img_h} - 30).

What is the SINGLE next action? Pick ONE:
- "tap": tap a specific point (give x, y on this image)
- "wait": wait for animation/loading (max 3 seconds)
- "done": goal is complete, or stuck and need to re-plan

Return ONLY valid JSON (no explanation):
{{
  "action": "tap/wait/done",
  "x": number (only for tap),
  "y": number (only for tap),
  "target": "what you're tapping (e.g. 'Upgrade button', 'Range building')",
  "reason": "why this moves toward the goal"
}}
"""


class ClaudeVision:
    def __init__(self, api_key=None):
        self.client = anthropic.Anthropic(
            api_key=api_key or config.ANTHROPIC_API_KEY
        )
        self.call_count = 0
        self.memory = GameStateMemory()

    def strategic_plan(self, screenshot_b64):
        """Sonnet: analyze game state, decide what goal to pursue"""
        self.call_count += 1

        prompt = STRATEGIC_PROMPT.format(
            strategy_knowledge=STRATEGY_KNOWLEDGE,
            strategic_context=self.memory.get_strategic_context(),
        )

        response = self.client.messages.create(
            model=config.STRATEGIC_MODEL,
            max_tokens=config.STRATEGIC_MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64", "media_type": "image/jpeg",
                        "data": screenshot_b64
                    }},
                    {"type": "text", "text": prompt}
                ]
            }]
        )

        raw = response.content[0].text.strip()
        result = self._parse_json(raw)

        # Update memory
        if result.get("power_visible"):
            self.memory.track_power(result["power_visible"])
        if result.get("tc_level_visible"):
            self.memory.update("tc_level", result["tc_level_visible"])
        if result.get("gems_visible"):
            self.memory.update("gems", result["gems_visible"])

        return result

    def tactical_step(self, screenshot_b64, img_w, img_h,
                      goal, goal_description, steps_taken,
                      last_action="none", last_result="starting"):
        """Haiku: decide the single next tap/action"""
        self.call_count += 1

        prompt = TACTICAL_PROMPT.format(
            goal=goal,
            goal_description=goal_description,
            steps_taken=steps_taken,
            last_action=last_action,
            last_result=last_result,
            img_w=img_w,
            img_h=img_h,
        )

        response = self.client.messages.create(
            model=config.TACTICAL_MODEL,
            max_tokens=config.TACTICAL_MAX_TOKENS,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64", "media_type": "image/jpeg",
                        "data": screenshot_b64
                    }},
                    {"type": "text", "text": prompt}
                ]
            }]
        )

        raw = response.content[0].text.strip()
        result = self._parse_json(raw)

        # Defaults
        result.setdefault("action", "wait")
        result.setdefault("target", "unknown")
        result.setdefault("reason", "")

        return result

    def _parse_json(self, raw):
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
                "reason": f"Failed to parse: {raw[:200]}"
            }
