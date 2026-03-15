# Cost Analysis

## The Problem

Using LLM vision APIs for every game decision is expensive:
- Screenshot every 3 seconds = 1,200 API calls/hour
- Claude Haiku at ~$0.001/call = **$1.20/hour = $864/month**
- Claude Sonnet at ~$0.004/call = **$4.80/hour = $3,456/month**

## Our Solution: Layered Architecture

By handling 98% of decisions locally (free), we reduce API costs to near-zero.

| Layer | Method | Cost | Frequency |
|-------|--------|------|-----------|
| Screen classify | Pixel analysis | FREE | Every 5s |
| Popup handling | FSM + coordinates | FREE | On detection |
| Timer tracking | World model | FREE | Continuous |
| Workflow execution | Scripted taps | FREE | On trigger |
| OCR state reading | PaddleOCR (local) | FREE | Every 60s |
| Strategic review | Claude Sonnet | $0.004 | Every 30 min |
| Tactical fallback | Claude Haiku | $0.001 | Rare (failures only) |

## Real-World Cost Breakdown

Running 24/7 for one month:

| Component | Calls/Month | Cost |
|-----------|-------------|------|
| Strategic reviews | ~1,440 (2/hr × 720hr) | $5.76 |
| Tactical fallbacks | ~200 (estimated) | $0.20 |
| **Total** | **~1,640** | **~$6/month** |

Compare: pure LLM approach = **$864/month** for the same task.

**Savings: 99.3%**

## How to Reduce Costs Further

1. **Better workflows** — fewer failures = fewer AI fallbacks
2. **Longer strategic intervals** — review every 60 min instead of 30 min
3. **Local LLM** — run Llama/Qwen locally for tactical steps (free but slower)
4. **Skip strategic reviews** — if world model is accurate, AI review adds little value
