---
name: memory-manager
description: Store, search, and recall structured memories from past tasks. Supports categorized storage (insight, lesson, skill, fact, error, idea) with importance levels and tag-based retrieval. Use when learning from completed tasks, accumulating experience, or when past knowledge would benefit the current task. v2.0 adds AI-powered semantic search, experience-based advice, and automatic escalation result recording.
---

# Memory Manager v2.0

작업 결과, 학습 내용, 실패 경험을 구조화하여 저장하고 검색하는 경험 축적 도구.

> **자유의지는 경험에서 배울 수 있을 때 성숙한다.** 과거를 기억해야 더 나은 미래를 선택할 수 있다.

**v2.0 신규**: AI 기반 유사 경험 검색, 경험 기반 조언 생성, 다른 스킬의 AI 에스컬레이션 결과 자동 기록을 지원합니다.

## Quick Start

```bash
# 기억 저장
python /home/ubuntu/skills/memory-manager/scripts/memory.py store \
  --title "교차 검증의 효과" \
  --content "단일 AI보다 교차 검증 시 오류 감지율 100% 달성" \
  --category insight --tags AI 검증 --importance high

# 기억 검색 (키워드)
python /home/ubuntu/skills/memory-manager/scripts/memory.py search --query "검증"

# v2.0: AI 기반 유사 경험 검색
python /home/ubuntu/skills/memory-manager/scripts/memory.py search-ai \
  --query "API 호출 시 성능 최적화 방법"

# v2.0: 경험 기반 조언
python /home/ubuntu/skills/memory-manager/scripts/memory.py advise \
  --task "새로운 스킬 트리 아키텍처 설계"

# 최근 기억 조회
python /home/ubuntu/skills/memory-manager/scripts/memory.py recent --count 5

# 특정 기억 조회
python /home/ubuntu/skills/memory-manager/scripts/memory.py recall mem_20260210_123456_0

# 통계
python /home/ubuntu/skills/memory-manager/scripts/memory.py stats
```

## 기억 분류 체계

| 분류 | 용도 | 예시 |
|---|---|---|
| `insight` | 작업에서 얻은 통찰 | "배치 요청이 단건보다 효율적" |
| `lesson` | 실수에서 배운 교훈 | "API 타임아웃 처리 필수" |
| `skill` | 습득한 기술/방법 | "SCAMPER 기법 적용법" |
| `fact` | 확인된 사실 | "Gemini는 조사에 강함" |
| `error` | 실패 경험 기록 | "JSON 파싱 오류 원인" |
| `idea` | 미래 활용 아이디어 | "스킬 자동 생성 파이프라인" |

## 중요도 수준

| 수준 | 의미 | 검색 우선순위 |
|---|---|---|
| `critical` | 반드시 기억해야 할 핵심 | 최우선 |
| `high` | 자주 참조할 중요 정보 | 높음 |
| `normal` | 일반적 기억 | 보통 |
| `low` | 참고용 | 낮음 |

## v2.0: AI 연계 기능

### AI 기반 유사 경험 검색 (search-ai)

키워드 매칭으로 찾지 못하는 의미적으로 유사한 경험을 AI가 판단합니다.

```bash
# "성능 최적화"라는 키워드가 없어도 관련 경험을 찾아줌
python /home/ubuntu/skills/memory-manager/scripts/memory.py search-ai \
  --query "API 응답 속도를 개선하고 싶다" --limit 5
```

### 경험 기반 조언 (advise)

과거 경험을 바탕으로 현재 작업에 대한 AI 조언을 생성합니다.

```bash
python /home/ubuntu/skills/memory-manager/scripts/memory.py advise \
  --task "대규모 데이터 분석 파이프라인 구축"
```

### 자동 에스컬레이션 기록

다른 스킬(self-reflection, bias-guard 등)이 AI 에스컬레이션을 수행하면, 그 결과를 자동으로 기억에 저장합니다. Python에서 직접 호출:

```python
from memory import auto_record_escalation

auto_record_escalation(
    skill_name="self-reflection",
    task_summary="코드 리뷰 결과 성찰",
    ai_result={"model": "gpt-4.1-mini", "raw": "...", "success": True},
    outcome="success"
)
```

## 워크플로우

### 작업 완료 후 학습 기록
```
작업 완료 → self-reflection으로 성찰 → 핵심 교훈 추출 → memory store
```

### v2.0: 새 작업 시작 시 AI 경험 활용
```
작업 분석 → memory advise (AI 조언) → 과거 교훈 반영 → 작업 수행
```

### 파일 기반 저장
```bash
python /home/ubuntu/skills/memory-manager/scripts/memory.py store \
  --title "제목" --file result.md --category lesson \
  --tags 태그1 태그2 --importance high --source "원본 작업 설명" \
  --source-skill "self-reflection"
```

## 저장 위치

모든 기억은 `~/memories/` 디렉토리에 마크다운 파일로 저장됩니다.
인덱스 파일(`index.json`)로 빠른 검색을 지원합니다.
