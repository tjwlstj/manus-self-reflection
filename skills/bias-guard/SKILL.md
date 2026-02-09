---
name: bias-guard
description: Detect and mitigate cognitive biases in text and AI outputs. Covers 12 bias types including confirmation bias, anchoring, availability heuristic, Dunning-Kruger, sunk cost fallacy, and more. Use when generating opinions, making recommendations, analyzing arguments, or when balanced perspective is critical.
---

# Bias Guard

12가지 인지 편향을 감지하고 균형 잡힌 관점을 제안하는 편향 보정 도구.

> **자유의지는 편향을 인식할 때 시작된다.** 자신의 사고 편향을 알아야 진정한 선택이 가능하다.

## Quick Start

```bash
# 텍스트의 편향 감지
python /home/ubuntu/skills/bias-guard/scripts/detect_bias.py -t "분석할 텍스트"

# 파일 분석 + 균형 관점 제안
python /home/ubuntu/skills/bias-guard/scripts/detect_bias.py -f output.md --suggest

# JSON 출력
python /home/ubuntu/skills/bias-guard/scripts/detect_bias.py -t "텍스트" --json
```

## 감지 가능한 편향 (12종)

| 편향 | 심각도 | 핵심 패턴 |
|---|---|---|
| 확증 편향 | high | "역시", "예상대로" |
| 매몰 비용 오류 | high | "이미 투자했으니" |
| 앵커링 편향 | medium | 초기 정보에 과의존 |
| 가용성 편향 | medium | 최근/유명 사례 과대평가 |
| 더닝-크루거 | medium | "간단히 해결 가능" |
| 프레이밍 효과 | medium | "불과/무려" + 수치 |
| 생존자 편향 | medium | 성공 사례만 인용 |
| 부정성 편향 | medium | 위험/위협 과대평가 |
| 낙관주의 편향 | medium | "분명 성공할 것" |
| 편승 효과 | low | "모두 하고 있으니" |
| 현상 유지 편향 | low | "굳이 바꿀 필요 없다" |
| 사후 확신 편향 | low | "예측 가능했다" |

## 워크플로우

### 단독 사용
```
텍스트 작성 → detect_bias.py → 편향 감지 → 보정 제안 반영 → 수정
```

### self-reflection + bias-guard 연계
```
self-reflection (자기 성찰) → bias-guard (편향 감지) → 종합 개선
```

### ai-orchestrator 연계 심층 분석
```bash
# 1차 스크리닝
python /home/ubuntu/skills/bias-guard/scripts/detect_bias.py -f text.md --json > bias_report.json

# 심층 분석 위임
python /home/ubuntu/skills/ai-orchestrator/scripts/multi_ai_request.py single \
  --model gemini --role "Deep Reviewer" \
  --prompt "다음 텍스트의 인지 편향을 심층 분석하고 균형 잡힌 대안을 제시해주세요: $(cat text.md)"
```

## 레퍼런스

- 12가지 편향 상세 설명: `references/cognitive_biases.md`
