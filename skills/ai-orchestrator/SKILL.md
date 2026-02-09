---
name: ai-orchestrator
description: Orchestrate multiple AI models (Gemini, GPT) by assigning specialized roles and coordinating their outputs. Use this skill when a task benefits from combining different AI strengths — such as broad research (Gemini), code generation or deep analysis (GPT), and cross-verification between models. Also use when the user explicitly requests multi-AI collaboration or wants to leverage external AI APIs.
---

# AI Orchestrator

Coordinate Gemini and GPT as specialized team members. Manus acts as the orchestrator — decomposing tasks, assigning roles, and synthesizing results.

## Core Principle

> **Gemini researches. GPT implements. Manus orchestrates.**

Each AI has distinct strengths. Never send the same generic prompt to all models. Instead, craft role-specific prompts that leverage each model's advantages.

## Quick Reference: Model-Role Mapping

| Need | Use | Role |
|---|---|---|
| Broad research, trends, summaries | Gemini | `Broad Researcher` |
| Code generation, debugging | GPT | `Code Specialist` |
| Verify facts, check accuracy | Gemini | `Fact Checker` |
| Analyze logic, find fallacies | GPT | `Logic Analyzer` |
| Critical review of any output | GPT | `Deep Reviewer` |
| Creative ideation | Gemini | `Idea Generator` |
| Technical documentation | GPT | `Technical Writer` |
| Validate another AI's output | Either | `Cross Verifier` |

For full role definitions and custom role creation, see `references/roles_and_models.md`.

## Standard Workflow

### Step 1: Analyze & Decompose

Break the user's goal into sub-tasks. For each sub-task, determine:
- Which AI model is best suited (see table above)
- What role to assign
- What specific prompt to craft

### Step 2: Dispatch Requests

Use the helper script to send role-assigned prompts:

```bash
# Single request
python scripts/multi_ai_request.py single \
  --model gemini --role "Broad Researcher" \
  --prompt "조사할 내용..." --output result.md

# Batch requests from config
python scripts/multi_ai_request.py batch \
  --config config.json --output-dir ./results/
```

Batch config format:
```json
{
  "requests": [
    {"model": "gemini", "role": "Broad Researcher", "prompt": "..."},
    {"model": "gpt", "role": "Code Specialist", "prompt": "..."}
  ],
  "cross_verify": [
    {"source_index": 1, "verifier_model": "gemini"}
  ]
}
```

See `references/batch_config_example.json` for a complete example.

### Step 3: Cross-Verify

Always cross-verify critical outputs. Send one AI's result to the other for review:

```bash
python scripts/multi_ai_request.py verify \
  --input result_gpt_code_specialist.md \
  --verifier gemini --output verification.md
```

### Step 4: Synthesize

Manus reads all results and verifications, then:
1. Resolves conflicts between AI outputs
2. Incorporates verification feedback
3. Produces the final unified result for the user

## Role Advisor

When unsure which model/role to assign, use the advisor:

```bash
python scripts/role_advisor.py \
  --task "사용자의 작업 설명" \
  --generate-config --output advice.json
```

This analyzes the task and recommends a workflow with model/role assignments.

## Prompt Crafting Guidelines

1. **Be role-specific**: Include the task context relevant to that role only
2. **Chain results**: Pass Gemini's research output as context to GPT's implementation prompt
3. **Request structured output**: Ask for JSON, tables, or numbered lists for easier synthesis
4. **Set scope**: Explicitly state what to include and exclude

Example of chaining:
```
Phase 1 (Gemini/Researcher): "Survey WebSocket libraries for Python..."
Phase 2 (GPT/Coder): "Based on this research: [Gemini's output]. Implement a chat server using FastAPI WebSocket..."
Phase 3 (Gemini/Verifier): "Review this code: [GPT's output]. Check for compatibility issues..."
```

## Dynamic Role Assignment

This skill supports creating new roles on-the-fly via custom system prompts:

```bash
python scripts/multi_ai_request.py single \
  --model gpt --role "Custom Role" \
  --prompt "..."
  # The script accepts any role name; unknown roles use a neutral system prompt.
  # For custom behavior, use the batch config with "system_prompt" field.
```

## When to Use This Skill

- User asks to "use multiple AIs" or "compare AI outputs"
- Task has both research and implementation components
- High-stakes output that benefits from cross-verification
- Complex tasks requiring different expertise types
- User wants to leverage Gemini for research and GPT for code

## Extending This Skill

To add new AI models or roles:
1. Add model profile to `MODEL_PROFILES` in `scripts/multi_ai_request.py`
2. Add role system prompt to `ROLE_SYSTEM_PROMPTS`
3. Update `references/roles_and_models.md`
