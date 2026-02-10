---
name: ai-orchestrator
description: Orchestrate multiple AI models (Gemini, GPT) by assigning specialized roles and coordinating their outputs. Use this skill when a task benefits from combining different AI strengths — such as broad research (Gemini), code generation or deep analysis (GPT), and cross-verification between models. Also use when the user explicitly requests multi-AI collaboration or wants to leverage external AI APIs. v2.0 adds auto_dispatch for proactive AI invocation based on context analysis.
---

# AI Orchestrator v2.0

Coordinate Gemini and GPT as specialized team members. Manus acts as the orchestrator — decomposing tasks, assigning roles, and synthesizing results.

**v2.0 신규**: `auto_dispatch.py` — 맥락을 분석하여 능동적으로 최적의 AI를 선택하고 호출하는 자동 판단 엔진.

## Core Principle

> **Gemini researches. GPT implements. Manus orchestrates. auto_dispatch decides.**

Each AI has distinct strengths. Never send the same generic prompt to all models. Instead, craft role-specific prompts that leverage each model's advantages. In v2.0, `auto_dispatch` can make this decision automatically.

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

## v2.0: 능동적 AI 디스패치 (auto_dispatch)

### 자동 판단 모드 (가장 능동적)

맥락을 분석하여 AI 호출 필요성, 최적 모델, 역할, 파이프라인을 자동 결정:

```bash
# 완전 자동 — 맥락 분석 → 전략 결정 → AI 호출 → 결과 반환
python scripts/auto_dispatch.py auto \
  --text "분석할 내용..." --goal "작업 목표"

# 맥락 분석만 (AI 호출 없이 판단만)
python scripts/auto_dispatch.py analyze \
  --text "분석할 내용..."

# 파이프라인 강제 지정
python scripts/auto_dispatch.py pipeline \
  --text "내용..." --force-pipeline cross_verify
```

### 자동 판단 기준

auto_dispatch는 다음을 자동으로 평가합니다:

| 평가 항목 | 설명 | AI 호출 임계값 |
|---|---|---|
| 작업 유형 | 사실 검증, 인과 추론, 창의적 생성 등 7종 분류 | 유형별 가중치 합산 |
| 불확실성 | 질문형, 추측 표현, 논란 표현 감지 | 점수 3 이상 |
| 복잡도 | 접속사, 다층적 표현, 텍스트 길이 | 점수 4 이상 |
| AI 필요성 | 위 3가지의 종합 점수 | 총점 3 이상 |

### 파이프라인 종류

| 파이프라인 | 설명 | 사용 조건 |
|---|---|---|
| `single` | 단일 AI 호출 | 낮은 복잡도 |
| `single_with_verify` | 1차 호출 + 품질 자동 평가 | 중간 복잡도 |
| `cross_verify` | 1차 호출 + 교차 검증 | 높은 불확실성 |
| `dual_generate` | 양쪽 모델 동시 생성 + 합성 | 창의적 작업 |

### 다른 스킬에서 auto_dispatch 호출

```python
# 다른 스킬의 스크립트에서 직접 임포트
sys.path.insert(0, "/home/ubuntu/skills/ai-orchestrator/scripts")
from auto_dispatch import execute_auto, analyze_context

# 맥락 분석만
context = analyze_context("분석할 텍스트", "작업 목표")
if context["needs_ai"]:
    result = execute_auto("텍스트", "목표")
```

## Standard Workflow (v1.0 호환)

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

## When to Use This Skill

- User asks to "use multiple AIs" or "compare AI outputs"
- Task has both research and implementation components
- High-stakes output that benefits from cross-verification
- Complex tasks requiring different expertise types
- User wants to leverage Gemini for research and GPT for code
- **v2.0**: Other skills trigger AI escalation (automatic)
- **v2.0**: Context analysis indicates high complexity or uncertainty

## Extending This Skill

To add new AI models or roles:
1. Add model profile to `MODEL_PROFILES` in `scripts/multi_ai_request.py`
2. Add role system prompt to `ROLE_SYSTEM_PROMPTS`
3. Update `references/roles_and_models.md`
4. **v2.0**: Add task type signals to `TASK_TYPE_SIGNALS` in `scripts/auto_dispatch.py`
