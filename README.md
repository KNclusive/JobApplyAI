# Job-Application-Agent
This repository host an job-application agent using LangChain and Playwright

The code works, possible remaining works:
1. Explore resolution for context bloating, Resolution is context optimisation for smaller models like llama 8B
2. Model choice selection.

The llama 8B model is failing for instruction execution and tool calling, this issue is registered and possible due to Ollama's system prompt.
Codestral is performing good, but big model and 18G ram is not enough, Look into quantisation or distillation
