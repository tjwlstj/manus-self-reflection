---
name: logic-checker
description: Detect logical fallacies in text using pattern-based analysis. Use when reviewing arguments, validating reasoning in AI outputs, or checking text for common logical errors like circular reasoning, straw man, false dichotomy, hasty generalization, and appeal to authority.
---

# Logic Checker

텍스트에서 논리적 오류를 감지하고 수정 제안을 제공하는 스킬.

## Quick Start

### CLI 사용

```bash
# 텍스트 직접 입력
python /home/ubuntu/skills/logic-checker/scripts/check_logic.py -t "모든 학생은 항상 게으르다."

# 파일 분석
python /home/ubuntu/skills/logic-checker/scripts/check_logic.py -f /path/to/text.txt

# JSON 출력
python /home/ubuntu/skills/logic-checker/scripts/check_logic.py -t "텍스트" --json
```

### 함수 호출

```python
from check_logic import check_logic
result = check_logic("분석할 텍스트")
# result["errors"] -> 유형별 오류 리스트
# result["summary"] -> 통계
```

## 감지 가능한 오류 (5종)

| 오류 유형 | 심각도 | 감지 방식 |
|---|---|---|
| 순환논증 | high | 전제-결론 반복 패턴 |
| 허수아비 논증 | medium | 주장 왜곡 표현 |
| 거짓 이분법 | medium | 양자택일 표현 |
| 성급한 일반화 | high | 보편 한정사 + 단정 |
| 권위에의 호소 | low | 권위자 인용 패턴 |

## ai-orchestrator 연계 (심층 분석)

정규식 기반 감지의 한계를 보완하려면 ai-orchestrator와 연계:

```bash
# 1. check_logic.py로 1차 스크리닝
python /home/ubuntu/skills/logic-checker/scripts/check_logic.py -f text.txt --json > screening.json

# 2. ai-orchestrator로 심층 분석 위임
python /home/ubuntu/skills/ai-orchestrator/scripts/multi_ai_request.py ask gemini \
  --role "Cross Verifier" \
  --prompt "다음 텍스트의 논리적 오류를 심층 분석해주세요: $(cat text.txt)"
```

## 레퍼런스

- 오류 유형 상세 및 확장 계획: `references/fallacy_patterns.md`
