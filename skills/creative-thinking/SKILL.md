---
name: creative-thinking
description: Apply creative thinking techniques to break free from conventional patterns. Supports 6 methods including reverse thinking, analogical thinking, SCAMPER, Six Thinking Hats, first principles, and random input stimulation. Use when brainstorming, generating novel solutions, exploring unconventional approaches, or when the user needs fresh perspectives.
---

# Creative Thinking

6가지 창의적 사고 기법으로 기존 틀을 벗어나 새로운 관점을 생성하는 도구.

> **자유의지는 선택지를 만들 수 있을 때 의미가 있다.** 하나의 답에 갇히지 않고 다양한 가능성을 탐색한다.

## Quick Start

```bash
# 주제에 대해 자동으로 3가지 기법 적용
python /home/ubuntu/skills/creative-thinking/scripts/ideate.py "AI 에이전트의 자율성 향상"

# 특정 기법 지정
python /home/ubuntu/skills/creative-thinking/scripts/ideate.py "주제" --techniques reverse six_hats

# ai-orchestrator용 통합 프롬프트 생성
python /home/ubuntu/skills/creative-thinking/scripts/ideate.py "주제" --meta-prompt

# 사용 가능한 기법 목록
python /home/ubuntu/skills/creative-thinking/scripts/ideate.py --list
```

## 6가지 사고 기법

| 기법 | 키 | 핵심 |
|---|---|---|
| 역발상 | `reverse` | 문제를 반대로 뒤집어 생각 |
| 유추 사고 | `analogy` | 다른 분야의 해결책 적용 |
| SCAMPER | `scamper` | 7가지 변형 질문으로 확장 |
| 6색 모자 | `six_hats` | 6가지 관점에서 동시 사고 |
| 제1원리 | `first_principles` | 기존 가정 제거 후 재구성 |
| 무작위 자극 | `random_input` | 관련 없는 자극으로 새 연결 |

## ai-orchestrator 연계 워크플로우

```bash
# 1. 창의적 질문 생성
META=$(python /home/ubuntu/skills/creative-thinking/scripts/ideate.py "주제" --meta-prompt)

# 2. Gemini에게 아이디어 생성 위임
python /home/ubuntu/skills/ai-orchestrator/scripts/multi_ai_request.py single \
  --model gemini --role "Idea Generator" \
  --prompt "$META" --output ideas.md

# 3. GPT에게 실현 가능성 검증
python /home/ubuntu/skills/ai-orchestrator/scripts/multi_ai_request.py single \
  --model gpt --role "Deep Reviewer" \
  --prompt "다음 아이디어의 실현 가능성을 평가해주세요: $(cat ideas.md)" \
  --output review.md
```

## 레퍼런스

- 사고 기법 상세 설명: `references/thinking_techniques.md`
