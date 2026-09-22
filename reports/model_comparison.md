# Model & Provider Comparison Analysis

## Providers Evaluated
1. **MockProvider / RuleBasedExtractor**:
   - Zero external dependencies or API keys required.
   - Deterministic regex & speaker grammar parsing.
   - Sub-second execution latency.
2. **OpenAIProvider (gpt-4o-mini)**:
   - High conversational comprehension and nuanced implicit assignment detection.
   - Requires network connectivity and valid API key.

## Architectural Trade-off Summary
| Dimension | Rule / Mock Provider | OpenAI Cloud Provider |
|---|---|---|
| Offline Capability | 100% Offline | Requires Internet & API Key |
| Latency | ~0.05 seconds | ~1.5 - 3.0 seconds |
| Cost | Free | Pay-per-token |
| Complex Paraphrasing | Pattern-dependent | Native semantic reasoning |
