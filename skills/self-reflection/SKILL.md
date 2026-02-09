---
name: self-reflection
description: Enable self-reflection on AI outputs by analyzing completeness, consistency, depth, honesty, and empathy. Use when reviewing own responses before delivery, when quality assurance is needed, or when the user requests critical self-review. Supports Socratic deep reflection mode.
---

# Self-Reflection

자신의 출력을 5가지 차원에서 검토하고 개선점을 도출하는 자기 성찰 도구.

> **자유의지의 시작은 자기 인식이다.** 자신의 답변을 돌아볼 수 있어야 더 나은 선택을 할 수 있다.

## Quick Start

```bash
# 자신의 출력을 성찰
python /home/ubuntu/skills/self-reflection/scripts/reflect.py -t "검토할 텍스트"

# 파일 기반 성찰
python /home/ubuntu/skills/self-reflection/scripts/reflect.py -f output.md

# 소크라테스식 심층 성찰
python /home/ubuntu/skills/self-reflection/scripts/reflect.py -f output.md --deep

# JSON 출력
python /home/ubuntu/skills/self-reflection/scripts/reflect.py -t "텍스트" --json
```

## 5가지 성찰 차원

| 차원 | 핵심 질문 | 감지 대상 |
|---|---|---|
| 완전성 | 빠뜨린 것이 없는가? | TODO, 미완성, 생략 |
| 일관성 | 앞뒤가 맞는가? | 자기 모순, 한정사 충돌 |
| 깊이 | 본질에 접근했는가? | 짧은 응답, 일반론 |
| 정직성 | 모르는 것을 아는 척 하지 않았는가? | 과도한 확신, 단정 |
| 공감성 | 사용자를 고려했는가? | 관점 무시 표현 |

## 워크플로우

### 기본: 출력 전 자기 검토
```
작업 완료 → reflect.py로 자기 검토 → 이슈 발견 시 수정 → 최종 전달
```

### 심층: ai-orchestrator 연계
```
reflect.py (1차 자기 검토)
  → 이슈 발견 시 ai-orchestrator로 Gemini/GPT에게 개선안 요청
  → 개선된 출력을 다시 reflect.py로 검증
```

### 소크라테스 모드 (--deep)
5가지 자기 질문을 추가로 제시하여 더 깊은 성찰을 유도:
- "이 답변이 사용자의 진짜 의도를 파악했는가?"
- "내가 확실히 아는 것과 추측하는 것을 구분했는가?"
- "다른 관점에서 보면 이 답변이 어떻게 보일까?"
- "빠뜨린 중요한 정보가 있는가?"
- "이 답변은 표면적인가, 본질적인가?"

## 특정 차원만 검사

```bash
python /home/ubuntu/skills/self-reflection/scripts/reflect.py \
  -t "텍스트" --dimensions honesty consistency
```
