---
name: bias-guard
description: Detect and mitigate cognitive biases in text and AI outputs. Covers 12 bias types including confirmation bias, anchoring, availability heuristic, Dunning-Kruger, sunk cost fallacy, and more. Use when generating opinions, making recommendations, analyzing arguments, or when balanced perspective is critical. v2.0 adds automatic AI escalation when bias score falls below threshold.
---

# Bias Guard v2.0

12가지 인지 편향을 감지하고 균형 잡힌 관점을 제안하는 편향 보정 도구.

> **자유의지는 편향을 인식할 때 시작된다.** 자신의 사고 편향을 알아야 진정한 선택이 가능하다.

**v2.0 신규**: 편향 점수가 임계값(75점) 이하이면 자동으로 외부 AI에게 심층 편향 분석을 요청합니다.

## Quick Start

```bash
# 텍스트의 편향 감지
python /home/ubuntu/skills/bias-guard/scripts/detect_bias.py -t "분석할 텍스트"

# 파일 분석 + 균형 관점 제안
python /home/ubuntu/skills/bias-guard/scripts/detect_bias.py -f output.md --suggest

# v2.0: 강제 AI 에스컬레이션
python /home/ubuntu/skills/bias-guard/scripts/detect_bias.py -f output.md --escalate

# v2.0: AI 에스컬레이션 비활성화 (정규식만)
python /home/ubuntu/skills/bias-guard/scripts/detect_bias.py -t "텍스트" --no-escalate

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

## v2.0: AI 에스컬레이션

### 자동 에스컬레이션 조건

| 조건 | 임계값 | 동작 |
|---|---|---|
| 균형 점수 낮음 | 75점 이하 | AI 심층 분석 자동 요청 |
| 텍스트 길이 과다 | 2000자 이상 | 에스컬레이션 권장 |
| 편향 다수 감지 | 3건 이상 | 에스컬레이션 권장 |
| 강제 모드 | `--escalate` | 항상 AI 호출 |

### AI 심층 분석 내용

AI는 정규식이 감지하지 못하는 다음 항목을 추가 분석합니다:
- 미묘한 프레이밍 편향
- 문화적/맥락적 편향
- 복합 편향 (여러 편향의 상호작용)
- 구체적 보정 제안

## 워크플로우

### 단독 사용
```
텍스트 작성 → detect_bias.py → 편향 감지 → 보정 제안 반영 → 수정
```

### v2.0: 자동 에스컬레이션 포함
```
텍스트 작성 → detect_bias.py (정규식 1차)
  → 점수 75 이하? → 자동 AI 심층 분석
  → 정규식 + AI 결과 합성 → 보정 제안 → 수정
```

### self-reflection + bias-guard 연계
```
self-reflection (자기 성찰) → bias-guard (편향 감지) → 종합 개선
```

## 레퍼런스

- 12가지 편향 상세 설명: `references/cognitive_biases.md`
