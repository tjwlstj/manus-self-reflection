---
name: logic-checker
description: Detect logical fallacies in text using pattern-based analysis. Use when reviewing arguments, validating reasoning in AI outputs, or checking text for common logical errors like circular reasoning, straw man, false dichotomy, hasty generalization, and appeal to authority. v2.0 adds automatic AI escalation when multiple errors are detected.
---

# Logic Checker v2.0

텍스트에서 논리적 오류를 감지하고 수정 제안을 제공하는 스킬.

**v2.0 신규**: 오류가 2건 이상 감지되면 자동으로 외부 AI에게 심층 분석을 요청합니다.

## Quick Start

### CLI 사용

```bash
# 텍스트 직접 입력
python /home/ubuntu/skills/logic-checker/scripts/check_logic.py -t "모든 학생은 항상 게으르다."

# 파일 분석
python /home/ubuntu/skills/logic-checker/scripts/check_logic.py -f /path/to/text.txt

# v2.0: 강제 AI 에스컬레이션
python /home/ubuntu/skills/logic-checker/scripts/check_logic.py -f text.txt --escalate

# v2.0: AI 에스컬레이션 비활성화 (정규식만)
python /home/ubuntu/skills/logic-checker/scripts/check_logic.py -t "텍스트" --no-escalate

# JSON 출력
python /home/ubuntu/skills/logic-checker/scripts/check_logic.py -t "텍스트" --json
```

### 함수 호출

```python
from check_logic import check_logic, check_logic_hybrid

# v1.0 호환: 정규식만
result = check_logic("분석할 텍스트")

# v2.0: 하이브리드 (정규식 + 자동 AI)
result = check_logic_hybrid("분석할 텍스트")
```

## 감지 가능한 오류 (5종)

| 오류 유형 | 심각도 | 감지 방식 |
|---|---|---|
| 순환논증 | high | 전제-결론 반복 패턴 |
| 허수아비 논증 | medium | 주장 왜곡 표현 |
| 거짓 이분법 | medium | 양자택일 표현 |
| 성급한 일반화 | high | 보편 한정사 + 단정 |
| 권위에의 호소 | low | 권위자 인용 패턴 |

## v2.0: AI 에스컬레이션

### 자동 에스컬레이션 조건

| 조건 | 임계값 | 동작 |
|---|---|---|
| 오류 다수 감지 | 2건 이상 | AI 심층 분석 자동 요청 |
| 텍스트 길이 과다 | 2000자 이상 | 에스컬레이션 권장 |
| 강제 모드 | `--escalate` | 항상 AI 호출 |

### AI 심층 분석 내용

AI는 정규식이 감지하지 못하는 다음 항목을 추가 분석합니다:
- 숨겨진 전제
- 비형식적 오류
- 논증 구조의 약점
- 구체적 수정 제안

## 워크플로우

### v2.0: 자동 에스컬레이션 포함
```
텍스트 → check_logic.py (정규식 1차)
  → 오류 2건 이상? → 자동 AI 심층 분석
  → 정규식 + AI 결과 합성 → 수정 제안
```

### ai-orchestrator 연계 (수동 심층 분석)

```bash
# 1. check_logic.py로 1차 스크리닝
python /home/ubuntu/skills/logic-checker/scripts/check_logic.py -f text.txt --json > screening.json

# 2. ai-orchestrator의 auto_dispatch로 자동 심층 분석
python /home/ubuntu/skills/ai-orchestrator/scripts/auto_dispatch.py auto \
  --file text.txt --goal "논리적 오류 심층 분석"
```

## 레퍼런스

- 오류 유형 상세 및 확장 계획: `references/fallacy_patterns.md`
